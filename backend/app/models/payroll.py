from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Float, Enum, Text
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class SalaryDetail(BaseModel, TimestampMixin):
    """Salary detail model for employee compensation information."""
    __tablename__ = "salary_details"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    basic_salary = Column(Float, nullable=False)
    hra = Column(Float, default=0.0)
    da = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowances = Column(Float, default=0.0)
    pf_deduction = Column(Float, default=0.0)
    tax_deduction = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    effective_date = Column(Date, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="salary_details")


class Payroll(BaseModel, TimestampMixin):
    """Payroll model for monthly salary processing."""
    __tablename__ = "payroll"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    basic_salary = Column(Float, nullable=False)
    hra = Column(Float, default=0.0)
    da = Column(Float, default=0.0)
    transport_allowance = Column(Float, default=0.0)
    medical_allowance = Column(Float, default=0.0)
    other_allowances = Column(Float, default=0.0)
    total_earnings = Column(Float, nullable=False)
    pf_deduction = Column(Float, default=0.0)
    tax_deduction = Column(Float, default=0.0)
    other_deductions = Column(Float, default=0.0)
    total_deductions = Column(Float, default=0.0)
    net_salary = Column(Float, nullable=False)
    days_present = Column(Integer, default=0)
    days_absent = Column(Integer, default=0)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    processed_date = Column(DateTime)
    # Relationships
    employee = relationship("Employee", back_populates="payroll_records")
    payslips = relationship("Payslip", back_populates="payroll")
class Payslip(BaseModel, TimestampMixin):
    """Payslip model for generated salary slips."""
    __tablename__ = "payslips"
    
    payroll_id = Column(Integer, ForeignKey("payroll.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    file_path = Column(String(500))
    generated_date = Column(DateTime, nullable=False)
    
    # Relationships
    employee = relationship("Employee", back_populates="payslips")
    payroll = relationship("Payroll", back_populates="payslips")