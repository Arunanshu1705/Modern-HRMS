from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Date, Text, Enum
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
import enum
class EmployeeStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
class Employee(BaseModel, TimestampMixin):
    """Employee model for HR management."""
    __tablename__ = "employees"
    # Personal Information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    # Job Information
    employee_code = Column(String(50), unique=True, index=True, nullable=False)
    designation = Column(String(100))
    department_id = Column(Integer, ForeignKey("departments.id"))
    role_id = Column(Integer, ForeignKey("roles.id"))
    # Status
    status = Column(Enum(EmployeeStatus), default=EmployeeStatus.ACTIVE, nullable=False)
    join_date = Column(Date, nullable=False)
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    country = Column(String(100), default="USA")
    # Authentication
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    # Relationships
    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees")
    role = relationship("Role", back_populates="employees")
    # HR Relationships
    attendance_records = relationship("Attendance", back_populates="employee")
    leave_requests = relationship("LeaveRequest", back_populates="employee", foreign_keys="LeaveRequest.employee_id")
    leave_balances = relationship("LeaveBalance", back_populates="employee")
    salary_details = relationship("SalaryDetail", back_populates="employee")
    payroll_records = relationship("Payroll", back_populates="employee")
    payslips = relationship("Payslip", back_populates="employee")
    # Skills and Experience
    employee_skills = relationship("EmployeeSkill", back_populates="employee")
    employee_tools = relationship("EmployeeTool", back_populates="employee")
    employee_projects = relationship("EmployeeProject", back_populates="employee")
    work_experiences = relationship("WorkExperience", back_populates="employee")
    certifications = relationship("Certification", back_populates="employee")
    # Chatbot
    chat_sessions = relationship("ChatSession", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")