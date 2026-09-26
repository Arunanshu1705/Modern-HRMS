from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, Float, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
import enum


class LeaveType(BaseModel, TimestampMixin):
    """Leave type model for different categories of leave."""
    __tablename__ = "leave_types"
    
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text)
    days_allowed = Column(Integer, default=0, nullable=False)
    is_paid = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    leave_balances = relationship("LeaveBalance", back_populates="leave_type")
    leave_requests = relationship("LeaveRequest", back_populates="leave_type")


class LeaveStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveBalance(BaseModel, TimestampMixin):
    """Leave balance model for tracking employee leave entitlements."""
    __tablename__ = "leave_balances"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    year = Column(Integer, nullable=False)
    total_days = Column(Integer, default=0, nullable=False)
    used_days = Column(Integer, default=0, nullable=False)
    remaining_days = Column(Integer, default=0, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_balances")
    leave_type = relationship("LeaveType", back_populates="leave_balances")
    
    # Unique constraint
    __table_args__ = (
        UniqueConstraint('employee_id', 'leave_type_id', 'year', name='unique_employee_leave_year'),
    )


class LeaveRequest(BaseModel, TimestampMixin):
    """Leave request model for employee leave applications."""
    __tablename__ = "leave_requests"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type_id = Column(Integer, ForeignKey("leave_types.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_days = Column(Integer, default=0, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum(LeaveStatus), default=LeaveStatus.PENDING, nullable=False)
    approved_by = Column(Integer, ForeignKey("employees.id"))
    approved_date = Column(DateTime)
    rejection_reason = Column(Text)
    
    # Relationships
    employee = relationship("Employee", back_populates="leave_requests", foreign_keys="LeaveRequest.employee_id")
    leave_type = relationship("LeaveType", back_populates="leave_requests")
    approver = relationship("Employee", foreign_keys="LeaveRequest.approved_by")