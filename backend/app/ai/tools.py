from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models import (
    Attendance, LeaveBalance, LeaveRequest, LeaveType,
    Payroll, Payslip, Employee, Holiday, Announcement,
    EmployeeSkill, EmployeeTool, Department, Skill, Tool
)
from app.database.database import SessionLocal


class HRMSTools:
    """Safe backend tools/functions for AI chatbot to interact with HRMS data."""
    
    def __init__(self, user_id: str, user_role: str, employee_id: Optional[int] = None):
        self.user_id = user_id
        self.user_role = user_role
        self.employee_id = employee_id
        self.db = SessionLocal()
    
    def __del__(self):
        """Close database session."""
        self.db.close()
    
    # Employee-specific tools
    def get_my_attendance(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict[str, Any]:
        """Get current employee's attendance records."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        query = self.db.query(Attendance).filter(Attendance.employee_id == self.employee_id)
        
        if start_date:
            from sqlalchemy import func
            query = query.filter(func.date(Attendance.date) >= start_date)
        
        if end_date:
            from sqlalchemy import func
            query = query.filter(func.date(Attendance.date) <= end_date)
        
        attendance_records = query.order_by(Attendance.date.desc()).limit(30).all()
        
        return {
            "attendance": [
                {
                    "date": att.date.isoformat(),
                    "check_in": att.check_in.strftime("%H:%M:%S") if att.check_in else None,
                    "check_out": att.check_out.strftime("%H:%M:%S") if att.check_out else None,
                    "working_hours": att.working_hours,
                    "status": att.status.value
                }
                for att in attendance_records
            ]
        }
    
    def get_my_leave_balance(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get current employee's leave balance."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        target_year = year or datetime.now().year
        
        balances = self.db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == self.employee_id,
            LeaveBalance.year == target_year
        ).all()
        
        result = []
        for balance in balances:
            leave_type = self.db.query(LeaveType).filter(LeaveType.id == balance.leave_type_id).first()
            result.append({
                "leave_type": leave_type.name if leave_type else "Unknown",
                "total_days": balance.total_days,
                "used_days": balance.used_days,
                "remaining_days": balance.remaining_days
            })
        
        return {"leave_balance": result}
    
    def get_my_leave_history(self, status_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get current employee's leave history."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        query = self.db.query(LeaveRequest).filter(LeaveRequest.employee_id == self.employee_id)
        
        if status_filter:
            query = query.filter(LeaveRequest.status == status_filter)
        
        requests = query.order_by(LeaveRequest.created_at.desc()).limit(20).all()
        
        return {
            "leave_requests": [
                {
                    "leave_type": leave_type.name if (leave_type := self.db.query(LeaveType).filter(LeaveType.id == req.leave_type_id).first()) else "Unknown",
                    "start_date": req.start_date.isoformat(),
                    "end_date": req.end_date.isoformat(),
                    "total_days": req.total_days,
                    "reason": req.reason,
                    "status": req.status.value
                }
                for req in requests
            ]
        }
    
    def get_my_payroll(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get current employee's payroll history."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        query = self.db.query(Payroll).filter(Payroll.employee_id == self.employee_id)
        
        if year:
            query = query.filter(Payroll.year == year)
        
        payroll_records = query.order_by(Payroll.year.desc(), Payroll.month.desc()).limit(12).all()
        
        return {
            "payroll": [
                {
                    "month": payroll.month,
                    "year": payroll.year,
                    "net_salary": payroll.net_salary,
                    "status": payroll.status.value
                }
                for payroll in payroll_records
            ]
        }
    
    def get_my_payslips(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get current employee's payslips."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        query = self.db.query(Payslip).filter(Payslip.employee_id == self.employee_id)
        
        if year:
            query = query.filter(Payslip.year == year)
        
        payslips = query.order_by(Payslip.year.desc(), Payslip.month.desc()).limit(12).all()
        
        return {
            "payslips": [
                {
                    "month": payslip.month,
                    "year": payslip.year,
                    "generated_date": payslip.generated_date.isoformat(),
                    "file_available": bool(payslip.file_path)
                }
                for payslip in payslips
            ]
        }
    
    def get_my_skills(self) -> Dict[str, Any]:
        """Get current employee's skills."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        employee_skills = self.db.query(EmployeeSkill).filter(
            EmployeeSkill.employee_id == self.employee_id
        ).all()
        
        result = []
        for emp_skill in employee_skills:
            skill = self.db.query(Skill).filter(Skill.id == emp_skill.skill_id).first()
            result.append({
                "skill": skill.name if skill else "Unknown",
                "proficiency_level": emp_skill.proficiency_level,
                "years_of_experience": emp_skill.years_of_experience
            })
        
        return {"skills": result}
    
    def get_my_tools(self) -> Dict[str, Any]:
        """Get current employee's tools."""
        if not self.employee_id:
            return {"error": "Employee profile not found"}
        
        employee_tools = self.db.query(EmployeeTool).filter(
            EmployeeTool.employee_id == self.employee_id
        ).all()
        
        result = []
        for emp_tool in employee_tools:
            tool = self.db.query(Tool).filter(Tool.id == emp_tool.tool_id).first()
            result.append({
                "tool": tool.name if tool else "Unknown",
                "proficiency_level": emp_tool.proficiency_level,
                "years_of_experience": emp_tool.years_of_experience
            })
        
        return {"tools": result}
    
    # General tools (accessible by both roles)
    def get_holidays(self, year: Optional[int] = None) -> Dict[str, Any]:
        """Get holidays."""
        query = self.db.query(Holiday).filter(Holiday.is_active == True)
        
        if year:
            from sqlalchemy import extract
            query = query.filter(extract('year', Holiday.date) == year)
        
        holidays = query.order_by(Holiday.date.asc()).limit(50).all()
        
        return {
            "holidays": [
                {
                    "name": holiday.name,
                    "date": holiday.date.isoformat(),
                    "holiday_type": holiday.holiday_type,
                    "description": holiday.description
                }
                for holiday in holidays
            ]
        }
    
    def get_announcements(self, priority_filter: Optional[str] = None) -> Dict[str, Any]:
        """Get announcements."""
        query = self.db.query(Announcement).filter(Announcement.is_active == True)
        
        # Filter out expired announcements
        query = query.filter(
            (Announcement.expiry_date.is_(None)) | (Announcement.expiry_date > datetime.utcnow())
        )
        
        if priority_filter:
            query = query.filter(Announcement.priority == priority_filter)
        
        announcements = query.order_by(Announcement.published_date.desc()).limit(20).all()
        
        return {
            "announcements": [
                {
                    "title": announcement.title,
                    "content": announcement.content,
                    "priority": announcement.priority.value,
                    "published_date": announcement.published_date.isoformat()
                }
                for announcement in announcements
            ]
        }
    
    # Admin-only tools
    def search_employees(self, name: str) -> Dict[str, Any]:
        """Search employees by name (admin only)."""
        if self.user_role != "admin":
            return {"error": "Unauthorized access"}
        
        from sqlalchemy import or_
        employees = self.db.query(Employee).filter(
            Employee.is_active == True,
            or_(
                Employee.first_name.ilike(f"%{name}%"),
                Employee.last_name.ilike(f"%{name}%")
            )
        ).limit(20).all()
        
        return {
            "employees": [
                {
                    "id": emp.id,
                    "name": f"{emp.first_name} {emp.last_name}",
                    "employee_code": emp.employee_code,
                    "email": emp.email,
                    "department": emp.department.name if emp.department else "N/A",
                    "designation": emp.designation or "N/A"
                }
                for emp in employees
            ]
        }
    
    def get_employee(self, employee_id: int) -> Dict[str, Any]:
        """Get specific employee details (admin only)."""
        if self.user_role != "admin":
            return {"error": "Unauthorized access"}
        
        employee = self.db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            return {"error": "Employee not found"}
        
        return {
            "employee": {
                "id": employee.id,
                "name": f"{employee.first_name} {employee.last_name}",
                "employee_code": employee.employee_code,
                "email": employee.email,
                "phone": employee.phone,
                "department": employee.department.name if employee.department else "N/A",
                "designation": employee.designation or "N/A",
                "status": employee.status.value,
                "join_date": employee.join_date.isoformat() if employee.join_date else None
            }
        }
    
    def get_pending_leave_requests(self) -> Dict[str, Any]:
        """Get pending leave requests (admin only)."""
        if self.user_role != "admin":
            return {"error": "Unauthorized access"}
        
        from app.models import LeaveStatus
        requests = self.db.query(LeaveRequest).filter(
            LeaveRequest.status == LeaveStatus.PENDING
        ).order_by(LeaveRequest.created_at.asc()).limit(20).all()
        
        result = []
        for request in requests:
            employee = self.db.query(Employee).filter(Employee.id == request.employee_id).first()
            leave_type = self.db.query(LeaveType).filter(LeaveType.id == request.leave_type_id).first()
            
            result.append({
                "request_id": request.id,
                "employee_name": f"{employee.first_name} {employee.last_name}" if employee else "Unknown",
                "employee_code": employee.employee_code if employee else "Unknown",
                "leave_type": leave_type.name if leave_type else "Unknown",
                "start_date": request.start_date.isoformat(),
                "end_date": request.end_date.isoformat(),
                "total_days": request.total_days,
                "reason": request.reason
            })
        
        return {"pending_requests": result}
    
    def get_attendance_overview(self, date_filter: Optional[date] = None) -> Dict[str, Any]:
        """Get attendance overview (admin only)."""
        if self.user_role != "admin":
            return {"error": "Unauthorized access"}
        
        target_date = date_filter or datetime.now().date()
        
        # Get total active employees
        total_employees = self.db.query(Employee).filter(Employee.is_active == True).count()
        
        # Get present today
        from sqlalchemy import func, and_
        present_today = self.db.query(Attendance).filter(
            and_(
                func.date(Attendance.date) == target_date,
                Attendance.status == "present"
            )
        ).count()
        
        # Get absent today
        present_employee_ids = self.db.query(Attendance.employee_id).filter(
            func.date(Attendance.date) == target_date
        ).all()
        present_ids = [id[0] for id in present_employee_ids]
        absent_today = total_employees - len(present_ids)
        
        return {
            "date": target_date.isoformat(),
            "total_employees": total_employees,
            "present_today": present_today,
            "absent_today": absent_today
        }
    
    def get_departments(self) -> Dict[str, Any]:
        """Get all departments (admin only)."""
        if self.user_role != "admin":
            return {"error": "Unauthorized access"}
        
        departments = self.db.query(Department).filter(Department.is_active == True).all()
        
        return {
            "departments": [
                {
                    "id": dept.id,
                    "name": dept.name,
                    "code": dept.code,
                    "description": dept.description
                }
                for dept in departments
            ]
        }