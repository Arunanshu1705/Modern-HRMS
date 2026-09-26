from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.database.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.leave import (
    LeaveTypeCreate, LeaveTypeResponse,
    LeaveBalanceResponse,
    LeaveRequestCreate, LeaveRequestUpdate, LeaveRequestResponse, LeaveRequestDetail
)
from app.models import LeaveType, LeaveBalance, LeaveRequest, Employee, User, LeaveStatus

router = APIRouter()


# Leave Type endpoints (admin only)
@router.post("/types", response_model=LeaveTypeResponse)
async def create_leave_type(
    leave_type: LeaveTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new leave type (admin only)."""
    existing = db.query(LeaveType).filter(LeaveType.code == leave_type.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave type code already exists"
        )
    
    new_leave_type = LeaveType(**leave_type.model_dump())
    db.add(new_leave_type)
    db.commit()
    db.refresh(new_leave_type)
    
    return new_leave_type


@router.get("/types", response_model=List[LeaveTypeResponse])
async def get_leave_types(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get all leave types (admin only)."""
    leave_types = db.query(LeaveType).filter(LeaveType.is_active == True).all()
    return leave_types


# Leave Balance endpoints
@router.get("/balance", response_model=List[LeaveBalanceResponse])
async def get_my_leave_balance(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's leave balance."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    target_year = year or datetime.now().year
    
    balances = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == employee.id,
            LeaveBalance.year == target_year
        )
    ).all()
    
    # Add leave type names
    result = []
    for balance in balances:
        leave_type = db.query(LeaveType).filter(LeaveType.id == balance.leave_type_id).first()
        balance_dict = balance.__dict__.copy()
        balance_dict['leave_type_name'] = leave_type.name if leave_type else None
        result.append(LeaveBalanceResponse(**balance_dict))
    
    return result


@router.get("/balance/{employee_id}", response_model=List[LeaveBalanceResponse])
async def get_employee_leave_balance(
    employee_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get leave balance for a specific employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    target_year = year or datetime.now().year
    
    balances = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == target_year
        )
    ).all()
    
    # Add leave type names
    result = []
    for balance in balances:
        leave_type = db.query(LeaveType).filter(LeaveType.id == balance.leave_type_id).first()
        balance_dict = balance.__dict__.copy()
        balance_dict['leave_type_name'] = leave_type.name if leave_type else None
        result.append(LeaveBalanceResponse(**balance_dict))
    
    return result


# Leave Request endpoints
@router.post("/request", response_model=LeaveRequestResponse)
async def create_leave_request(
    leave_request: LeaveRequestCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new leave request."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Validate dates
    if leave_request.start_date > leave_request.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before or equal to end date"
        )
    
    # Calculate total days
    total_days = (leave_request.end_date - leave_request.start_date).days + 1
    
    # Check leave balance
    leave_balance = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == employee.id,
            LeaveBalance.leave_type_id == leave_request.leave_type_id,
            LeaveBalance.year == leave_request.start_date.year
        )
    ).first()
    
    if not leave_balance or leave_balance.remaining_days < total_days:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient leave balance"
        )
    
    # Check for conflicting leave requests
    conflicting = db.query(LeaveRequest).filter(
        and_(
            LeaveRequest.employee_id == employee.id,
            LeaveRequest.status.in_([LeaveStatus.PENDING, LeaveStatus.APPROVED]),
            LeaveRequest.start_date <= leave_request.end_date,
            LeaveRequest.end_date >= leave_request.start_date
        )
    ).first()
    
    if conflicting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Conflicting leave request exists for this period"
        )
    
    # Create leave request
    new_request = LeaveRequest(
        employee_id=employee.id,
        **leave_request.model_dump(),
        total_days=total_days
    )
    
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    
    return new_request


@router.get("/history", response_model=List[LeaveRequestResponse])
async def get_my_leave_history(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's leave history."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    query = db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee.id)
    
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)
    
    requests = query.order_by(LeaveRequest.created_at.desc()).limit(50).all()
    
    # Add employee and leave type names
    result = []
    for request in requests:
        leave_type = db.query(LeaveType).filter(LeaveType.id == request.leave_type_id).first()
        request_dict = request.__dict__.copy()
        request_dict['employee_name'] = f"{employee.first_name} {employee.last_name}"
        request_dict['leave_type_name'] = leave_type.name if leave_type else None
        result.append(LeaveRequestResponse(**request_dict))
    
    return result


@router.get("/pending", response_model=List[LeaveRequestDetail])
async def get_pending_leave_requests(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get all pending leave requests (admin only)."""
    requests = db.query(LeaveRequest).filter(
        LeaveRequest.status == LeaveStatus.PENDING
    ).order_by(LeaveRequest.created_at.asc()).all()
    
    # Add employee and leave type details
    result = []
    for request in requests:
        employee = db.query(Employee).filter(Employee.id == request.employee_id).first()
        leave_type = db.query(LeaveType).filter(LeaveType.id == request.leave_type_id).first()
        
        department_name = None
        if employee and employee.department:
            department_name = employee.department.name
        
        request_dict = request.__dict__.copy()
        request_dict['employee_name'] = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"
        request_dict['employee_code'] = employee.employee_code if employee else "Unknown"
        request_dict['department_name'] = department_name
        request_dict['leave_type_name'] = leave_type.name if leave_type else "Unknown"
        result.append(LeaveRequestDetail(**request_dict))
    
    return result


@router.put("/{request_id}/approve", response_model=LeaveRequestResponse)
async def approve_leave_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Approve a leave request (admin only)."""
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request is not pending"
        )
    
    # Get current admin employee
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    admin_employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    
    # Update leave request
    leave_request.status = LeaveStatus.APPROVED
    leave_request.approved_by = admin_employee.id if admin_employee else None
    leave_request.approved_date = datetime.utcnow()
    
    # Deduct from leave balance
    leave_balance = db.query(LeaveBalance).filter(
        and_(
            LeaveBalance.employee_id == leave_request.employee_id,
            LeaveBalance.leave_type_id == leave_request.leave_type_id,
            LeaveBalance.year == leave_request.start_date.year
        )
    ).first()
    
    if leave_balance:
        leave_balance.used_days += leave_request.total_days
        leave_balance.remaining_days -= leave_request.total_days
    
    db.commit()
    db.refresh(leave_request)
    
    return leave_request


@router.put("/{request_id}/reject", response_model=LeaveRequestResponse)
async def reject_leave_request(
    request_id: int,
    rejection_reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Reject a leave request (admin only)."""
    leave_request = db.query(LeaveRequest).filter(LeaveRequest.id == request_id).first()
    if not leave_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave request not found"
        )
    
    if leave_request.status != LeaveStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Leave request is not pending"
        )
    
    # Update leave request
    leave_request.status = LeaveStatus.REJECTED
    leave_request.rejection_reason = rejection_reason
    
    db.commit()
    db.refresh(leave_request)
    
    return leave_request


@router.get("/employee/{employee_id}", response_model=List[LeaveRequestResponse])
async def get_employee_leave_history(
    employee_id: int,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get leave history for a specific employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    query = db.query(LeaveRequest).filter(LeaveRequest.employee_id == employee_id)
    
    if status_filter:
        query = query.filter(LeaveRequest.status == status_filter)
    
    requests = query.order_by(LeaveRequest.created_at.desc()).limit(50).all()
    
    # Add employee and leave type names
    result = []
    for request in requests:
        leave_type = db.query(LeaveType).filter(LeaveType.id == request.leave_type_id).first()
        request_dict = request.__dict__.copy()
        request_dict['employee_name'] = f"{employee.first_name} {employee.last_name}"
        request_dict['leave_type_name'] = leave_type.name if leave_type else None
        result.append(LeaveRequestResponse(**request_dict))
    
    return result