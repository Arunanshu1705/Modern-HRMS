from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, date, time
from app.database.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.attendance import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse,
    CheckInResponse, CheckOutResponse, AttendanceOverview, AttendanceAnalytics
)
from app.models import Attendance, Employee, User

router = APIRouter()


@router.post("/check-in", response_model=CheckInResponse)
async def check_in(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark employee check-in."""
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
    
    # Check if already checked in today
    today = datetime.now().date()
    existing = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == employee.id,
            func.date(Attendance.date) == today
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in today"
        )
    
    # Create attendance record
    now = datetime.now()
    check_in_time = now.time()
    
    # Determine status based on check-in time (9:00 AM is late)
    status = "present"
    if check_in_time >= time(9, 0):
        status = "late"
    
    attendance = Attendance(
        employee_id=employee.id,
        date=now,
        check_in=check_in_time,
        status=status
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return CheckInResponse(
        message="Check-in successful",
        attendance=attendance
    )


@router.post("/check-out", response_model=CheckOutResponse)
async def check_out(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark employee check-out."""
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
    
    # Get today's attendance record
    today = datetime.now().date()
    attendance = db.query(Attendance).filter(
        and_(
            Attendance.employee_id == employee.id,
            func.date(Attendance.date) == today
        )
    ).first()
    
    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No check-in record found for today"
        )
    
    if attendance.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked out today"
        )
    
    # Update check-out time and calculate working hours
    now = datetime.now()
    check_out_time = now.time()
    attendance.check_out = check_out_time
    
    # Calculate working hours
    check_in_datetime = datetime.combine(today, attendance.check_in)
    check_out_datetime = datetime.combine(today, check_out_time)
    working_hours = (check_out_datetime - check_in_datetime).total_seconds() / 3600
    attendance.working_hours = round(working_hours, 2)
    
    db.commit()
    db.refresh(attendance)
    
    return CheckOutResponse(
        message="Check-out successful",
        attendance=attendance,
        working_hours=attendance.working_hours
    )


@router.get("/me", response_model=List[AttendanceResponse])
async def get_my_attendance(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's attendance history."""
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
    
    query = db.query(Attendance).filter(Attendance.employee_id == employee.id)
    
    if start_date:
        query = query.filter(func.date(Attendance.date) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Attendance.date) <= end_date)
    
    attendance_records = query.order_by(Attendance.date.desc()).limit(100).all()
    return attendance_records


@router.get("/overview", response_model=AttendanceOverview)
async def get_attendance_overview(
    date_filter: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get attendance overview (admin only)."""
    target_date = date_filter or datetime.now().date()
    
    # Get total active employees
    total_employees = db.query(Employee).filter(Employee.is_active == True).count()
    
    # Get present today
    present_today = db.query(Attendance).filter(
        and_(
            func.date(Attendance.date) == target_date,
            Attendance.status == "present"
        )
    ).count()
    
    # Get absent today (no attendance record)
    present_employee_ids = db.query(Attendance.employee_id).filter(
        func.date(Attendance.date) == target_date
    ).all()
    present_ids = [id[0] for id in present_employee_ids]
    absent_today = total_employees - len(present_ids)
    
    # Get late today
    late_today = db.query(Attendance).filter(
        and_(
            func.date(Attendance.date) == target_date,
            Attendance.status == "late"
        )
    ).count()
    
    # Get on leave today
    on_leave_today = db.query(Employee).filter(
        and_(
            Employee.is_active == True,
            Employee.status == "on_leave"
        )
    ).count()
    
    # Calculate average working hours
    avg_hours_result = db.query(func.avg(Attendance.working_hours)).filter(
        func.date(Attendance.date) == target_date
    ).first()
    average_working_hours = round(avg_hours_result[0] or 0, 2)
    
    return AttendanceOverview(
        total_employees=total_employees,
        present_today=present_today,
        absent_today=absent_today,
        late_today=late_today,
        on_leave_today=on_leave_today,
        average_working_hours=average_working_hours
    )


@router.get("/employee/{employee_id}", response_model=List[AttendanceResponse])
async def get_employee_attendance(
    employee_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get attendance for a specific employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    query = db.query(Attendance).filter(Attendance.employee_id == employee_id)
    
    if start_date:
        query = query.filter(func.date(Attendance.date) >= start_date)
    
    if end_date:
        query = query.filter(func.date(Attendance.date) <= end_date)
    
    attendance_records = query.order_by(Attendance.date.desc()).limit(100).all()
    return attendance_records


@router.get("/analytics", response_model=List[AttendanceAnalytics])
async def get_attendance_analytics(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get attendance analytics for all employees (admin only)."""
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    
    analytics = []
    for employee in employees:
        # Get attendance records for the period
        attendance_records = db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee.id,
                func.date(Attendance.date) >= start_date,
                func.date(Attendance.date) <= end_date
            )
        ).all()
        
        total_days = len(attendance_records)
        present_days = sum(1 for a in attendance_records if a.status == "present")
        absent_days = sum(1 for a in attendance_records if a.status == "absent")
        late_days = sum(1 for a in attendance_records if a.status == "late")
        on_leave_days = sum(1 for a in attendance_records if a.status == "half_day")
        
        total_hours = sum(a.working_hours for a in attendance_records)
        average_working_hours = round(total_hours / total_days, 2) if total_days > 0 else 0
        
        attendance_percentage = round((present_days / total_days) * 100, 2) if total_days > 0 else 0
        
        analytics.append(AttendanceAnalytics(
            employee_id=employee.id,
            employee_name=f"{employee.first_name} {employee.last_name}",
            total_days=total_days,
            present_days=present_days,
            absent_days=absent_days,
            late_days=late_days,
            on_leave_days=on_leave_days,
            average_working_hours=average_working_hours,
            attendance_percentage=attendance_percentage
        ))
    
    return analytics
