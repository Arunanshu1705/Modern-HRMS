from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeProfile
from app.models import Employee, Department, Role, User

router = APIRouter()


@router.post("/", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new employee (admin only)."""
    # Check if employee code already exists
    existing = db.query(Employee).filter(Employee.employee_code == employee.employee_code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee code already exists"
        )
    
    # Check if email already exists
    existing_email = db.query(Employee).filter(Employee.email == employee.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    # Verify department exists if provided
    if employee.department_id:
        department = db.query(Department).filter(Department.id == employee.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found"
            )
    
    # Verify role exists if provided
    if employee.role_id:
        role = db.query(Role).filter(Role.id == employee.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
    
    new_employee = Employee(**employee.model_dump())
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    
    return new_employee


@router.get("/", response_model=List[EmployeeResponse])
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    department_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get all employees (admin only)."""
    query = db.query(Employee).filter(Employee.is_active == True)
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    if status_filter:
        query = query.filter(Employee.status == status_filter)
    
    employees = query.offset(skip).limit(limit).all()
    return employees


@router.get("/me", response_model=EmployeeProfile)
async def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current employee's profile."""
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
    
    # Get department and role names
    department_name = None
    if employee.department:
        department_name = employee.department.name
    
    role_name = None
    if employee.role:
        role_name = employee.role.name
    
    return EmployeeProfile(
        **employee.__dict__,
        department_name=department_name,
        role_name=role_name
    )


@router.get("/{employee_id}", response_model=EmployeeProfile)
async def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get a specific employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Get department and role names
    department_name = None
    if employee.department:
        department_name = employee.department.name
    
    role_name = None
    if employee.role:
        role_name = employee.role.name
    
    return EmployeeProfile(
        **employee.__dict__,
        department_name=department_name,
        role_name=role_name
    )


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Update an employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if email is being updated and if it already exists
    if employee_update.email and employee_update.email != employee.email:
        existing_email = db.query(Employee).filter(Employee.email == employee_update.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    for field, value in employee_update.model_dump(exclude_unset=True).items():
        setattr(employee, field, value)
    
    db.commit()
    db.refresh(employee)
    
    return employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Deactivate an employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    employee.is_active = False
    employee.status = "inactive"
    db.commit()
    
    return {"message": "Employee deactivated successfully"}


@router.get("/search/by-name", response_model=List[EmployeeResponse])
async def search_employees_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Search employees by name (admin only)."""
    employees = db.query(Employee).filter(
        Employee.is_active == True,
        (Employee.first_name.ilike(f"%{name}%")) | (Employee.last_name.ilike(f"%{name}%"))
    ).limit(20).all()
    
    return employees