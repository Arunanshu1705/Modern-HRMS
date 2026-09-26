from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from typing import List, Optional
from datetime import datetime, date
from app.database.database import get_db
from app.core.dependencies import get_current_admin
from app.schemas.attendance import AttendanceAnalytics
from app.models import Attendance, LeaveRequest, Employee, Payroll, LeaveStatus

router = APIRouter()


@router.get("/attendance")
async def get_attendance_report(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Generate attendance report (admin only)."""
    query = db.query(Attendance).filter(
        func.date(Attendance.date) >= start_date,
        func.date(Attendance.date) <= end_date
    )
    
    attendance_records = query.all()
    
    # Calculate statistics
    total_records = len(attendance_records)
    present_count = sum(1 for a in attendance_records if a.status == "present")
    absent_count = sum(1 for a in attendance_records if a.status == "absent")
    late_count = sum(1 for a in attendance_records if a.status == "late")
    half_day_count = sum(1 for a in attendance_records if a.status == "half_day")
    
    total_hours = sum(a.working_hours for a in attendance_records)
    average_hours = round(total_hours / total_records, 2) if total_records > 0 else 0
    
    # Employee-wise breakdown
    employee_stats = {}
    for record in attendance_records:
        if record.employee_id not in employee_stats:
            employee = db.query(Employee).filter(Employee.id == record.employee_id).first()
            employee_stats[record.employee_id] = {
                "employee_id": record.employee_id,
                "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
                "employee_code": employee.employee_code if employee else "Unknown",
                "department": employee.department.name if employee and employee.department else "N/A",
                "total_days": 0,
                "present_days": 0,
                "absent_days": 0,
                "late_days": 0,
                "half_day_days": 0,
                "total_hours": 0
            }
        
        employee_stats[record.employee_id]["total_days"] += 1
        employee_stats[record.employee_id]["total_hours"] += record.working_hours
        
        if record.status == "present":
            employee_stats[record.employee_id]["present_days"] += 1
        elif record.status == "absent":
            employee_stats[record.employee_id]["absent_days"] += 1
        elif record.status == "late":
            employee_stats[record.employee_id]["late_days"] += 1
        elif record.status == "half_day":
            employee_stats[record.employee_id]["half_day_days"] += 1
    
    # Calculate attendance percentage for each employee
    for emp_id, stats in employee_stats.items():
        if stats["total_days"] > 0:
            stats["attendance_percentage"] = round((stats["present_days"] / stats["total_days"]) * 100, 2)
            stats["average_hours"] = round(stats["total_hours"] / stats["total_days"], 2)
        else:
            stats["attendance_percentage"] = 0
            stats["average_hours"] = 0
    
    return {
        "summary": {
            "total_records": total_records,
            "present_count": present_count,
            "absent_count": absent_count,
            "late_count": late_count,
            "half_day_count": half_day_count,
            "average_hours": average_hours,
            "attendance_percentage": round((present_count / total_records) * 100, 2) if total_records > 0 else 0
        },
        "employee_breakdown": list(employee_stats.values())
    }


@router.get("/leave")
async def get_leave_report(
    start_date: date,
    end_date: date,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Generate leave report (admin only)."""
    query = db.query(LeaveRequest).filter(
        LeaveRequest.start_date >= start_date,
        LeaveRequest.end_date <= end_date
    )
    
    leave_requests = query.all()
    
    # Calculate statistics
    total_requests = len(leave_requests)
    approved_count = sum(1 for r in leave_requests if r.status == LeaveStatus.APPROVED)
    rejected_count = sum(1 for r in leave_requests if r.status == LeaveStatus.REJECTED)
    pending_count = sum(1 for r in leave_requests if r.status == LeaveStatus.PENDING)
    cancelled_count = sum(1 for r in leave_requests if r.status == LeaveStatus.CANCELLED)
    
    total_leave_days = sum(r.total_days for r in leave_requests if r.status == LeaveStatus.APPROVED)
    
    # Leave type breakdown
    leave_type_stats = {}
    for request in leave_requests:
        if request.leave_type_id not in leave_type_stats:
            from app.models import LeaveType
            leave_type = db.query(LeaveType).filter(LeaveType.id == request.leave_type_id).first()
            leave_type_stats[request.leave_type_id] = {
                "leave_type_name": leave_type.name if leave_type else "Unknown",
                "total_requests": 0,
                "approved_requests": 0,
                "total_days": 0
            }
        
        leave_type_stats[request.leave_type_id]["total_requests"] += 1
        if request.status == LeaveStatus.APPROVED:
            leave_type_stats[request.leave_type_id]["approved_requests"] += 1
            leave_type_stats[request.leave_type_id]["total_days"] += request.total_days
    
    # Employee-wise breakdown
    employee_stats = {}
    for request in leave_requests:
        if request.employee_id not in employee_stats:
            employee = db.query(Employee).filter(Employee.id == request.employee_id).first()
            employee_stats[request.employee_id] = {
                "employee_id": request.employee_id,
                "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
                "employee_code": employee.employee_code if employee else "Unknown",
                "department": employee.department.name if employee and employee.department else "N/A",
                "total_requests": 0,
                "approved_requests": 0,
                "rejected_requests": 0,
                "pending_requests": 0,
                "total_leave_days": 0
            }
        
        employee_stats[request.employee_id]["total_requests"] += 1
        if request.status == LeaveStatus.APPROVED:
            employee_stats[request.employee_id]["approved_requests"] += 1
            employee_stats[request.employee_id]["total_leave_days"] += request.total_days
        elif request.status == LeaveStatus.REJECTED:
            employee_stats[request.employee_id]["rejected_requests"] += 1
        elif request.status == LeaveStatus.PENDING:
            employee_stats[request.employee_id]["pending_requests"] += 1
    
    return {
        "summary": {
            "total_requests": total_requests,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "pending_count": pending_count,
            "cancelled_count": cancelled_count,
            "total_leave_days": total_leave_days,
            "approval_rate": round((approved_count / total_requests) * 100, 2) if total_requests > 0 else 0
        },
        "leave_type_breakdown": list(leave_type_stats.values()),
        "employee_breakdown": list(employee_stats.values())
    }


@router.get("/employees")
async def get_employee_report(
    department_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Generate employee report (admin only)."""
    query = db.query(Employee).filter(Employee.is_active == True)
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    if status_filter:
        query = query.filter(Employee.status == status_filter)
    
    employees = query.all()
    
    # Calculate statistics
    total_employees = len(employees)
    active_employees = sum(1 for e in employees if e.status == "active")
    inactive_employees = sum(1 for e in employees if e.status == "inactive")
    on_leave_employees = sum(1 for e in employees if e.status == "on_leave")
    
    # Department breakdown
    department_stats = {}
    for employee in employees:
        dept_id = employee.department_id or 0
        if dept_id not in department_stats:
            dept_name = employee.department.name if employee.department else "Unassigned"
            department_stats[dept_id] = {
                "department_id": dept_id,
                "department_name": dept_name,
                "total_employees": 0,
                "active_employees": 0,
                "inactive_employees": 0,
                "on_leave_employees": 0
            }
        
        department_stats[dept_id]["total_employees"] += 1
        if employee.status == "active":
            department_stats[dept_id]["active_employees"] += 1
        elif employee.status == "inactive":
            department_stats[dept_id]["inactive_employees"] += 1
        elif employee.status == "on_leave":
            department_stats[dept_id]["on_leave_employees"] += 1
    
    # Role breakdown
    role_stats = {}
    for employee in employees:
        role_id = employee.role_id or 0
        if role_id not in role_stats:
            role_name = employee.role.name if employee.role else "Unassigned"
            role_stats[role_id] = {
                "role_id": role_id,
                "role_name": role_name,
                "count": 0
            }
        
        role_stats[role_id]["count"] += 1
    
    return {
        "summary": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "inactive_employees": inactive_employees,
            "on_leave_employees": on_leave_employees
        },
        "department_breakdown": list(department_stats.values()),
        "role_breakdown": list(role_stats.values()),
        "employee_list": [
            {
                "id": e.id,
                "employee_code": e.employee_code,
                "name": f"{e.first_name} {e.last_name}",
                "email": e.email,
                "department": e.department.name if e.department else "N/A",
                "designation": e.designation or "N/A",
                "status": e.status.value,
                "join_date": e.join_date.isoformat() if e.join_date else None
            }
            for e in employees
        ]
    }


@router.get("/payroll")
async def get_payroll_report(
    month: int,
    year: int,
    department_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Generate payroll report (admin only)."""
    query = db.query(Payroll).filter(
        Payroll.month == month,
        Payroll.year == year
    )
    
    payroll_records = query.all()
    
    # Calculate statistics
    total_records = len(payroll_records)
    total_basic_salary = sum(p.basic_salary for p in payroll_records)
    total_net_salary = sum(p.net_salary for p in payroll_records)
    total_deductions = sum(p.total_deductions for p in payroll_records)
    
    average_net_salary = round(total_net_salary / total_records, 2) if total_records > 0 else 0
    
    # Status breakdown
    processed_count = sum(1 for p in payroll_records if p.status == "processed")
    pending_count = sum(1 for p in payroll_records if p.status == "pending")
    failed_count = sum(1 for p in payroll_records if p.status == "failed")
    
    # Employee-wise breakdown
    employee_payroll = []
    for payroll in payroll_records:
        employee = db.query(Employee).filter(Employee.id == payroll.employee_id).first()
        employee_payroll.append({
            "employee_id": payroll.employee_id,
            "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
            "employee_code": employee.employee_code if employee else "Unknown",
            "department": employee.department.name if employee and employee.department else "N/A",
            "basic_salary": payroll.basic_salary,
            "total_earnings": payroll.total_earnings,
            "total_deductions": payroll.total_deductions,
            "net_salary": payroll.net_salary,
            "status": payroll.status.value,
            "days_present": payroll.days_present,
            "days_absent": payroll.days_absent
        })
    
    return {
        "summary": {
            "month": month,
            "year": year,
            "total_records": total_records,
            "total_basic_salary": total_basic_salary,
            "total_net_salary": total_net_salary,
            "total_deductions": total_deductions,
            "average_net_salary": average_net_salary,
            "processed_count": processed_count,
            "pending_count": pending_count,
            "failed_count": failed_count
        },
        "employee_breakdown": employee_payroll
    }
