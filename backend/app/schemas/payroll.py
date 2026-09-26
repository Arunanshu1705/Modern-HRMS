from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.payroll import PaymentStatus


class SalaryDetailBase(BaseModel):
    """Base salary detail schema."""
    basic_salary: float = Field(..., ge=0)
    hra: float = Field(default=0.0, ge=0)
    da: float = Field(default=0.0, ge=0)
    transport_allowance: float = Field(default=0.0, ge=0)
    medical_allowance: float = Field(default=0.0, ge=0)
    other_allowances: float = Field(default=0.0, ge=0)
    pf_deduction: float = Field(default=0.0, ge=0)
    tax_deduction: float = Field(default=0.0, ge=0)
    other_deductions: float = Field(default=0.0, ge=0)
    effective_date: date


class SalaryDetailCreate(SalaryDetailBase):
    """Schema for creating salary detail."""
    employee_id: int


class SalaryDetailUpdate(BaseModel):
    """Schema for updating salary detail."""
    basic_salary: Optional[float] = Field(None, ge=0)
    hra: Optional[float] = Field(None, ge=0)
    da: Optional[float] = Field(None, ge=0)
    transport_allowance: Optional[float] = Field(None, ge=0)
    medical_allowance: Optional[float] = Field(None, ge=0)
    other_allowances: Optional[float] = Field(None, ge=0)
    pf_deduction: Optional[float] = Field(None, ge=0)
    tax_deduction: Optional[float] = Field(None, ge=0)
    other_deductions: Optional[float] = Field(None, ge=0)
    effective_date: Optional[date] = None


class SalaryDetailResponse(SalaryDetailBase):
    """Schema for salary detail response."""
    id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PayrollBase(BaseModel):
    """Base payroll schema."""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)
    basic_salary: float = Field(..., ge=0)
    hra: float = Field(default=0.0, ge=0)
    da: float = Field(default=0.0, ge=0)
    transport_allowance: float = Field(default=0.0, ge=0)
    medical_allowance: float = Field(default=0.0, ge=0)
    other_allowances: float = Field(default=0.0, ge=0)
    total_earnings: float = Field(..., ge=0)
    pf_deduction: float = Field(default=0.0, ge=0)
    tax_deduction: float = Field(default=0.0, ge=0)
    other_deductions: float = Field(default=0.0, ge=0)
    total_deductions: float = Field(..., ge=0)
    net_salary: float = Field(..., ge=0)
    days_present: int = Field(default=0, ge=0)
    days_absent: int = Field(default=0, ge=0)
    status: PaymentStatus = PaymentStatus.PENDING


class PayrollCreate(PayrollBase):
    """Schema for creating payroll."""
    employee_id: int


class PayrollUpdate(BaseModel):
    """Schema for updating payroll."""
    status: Optional[PaymentStatus] = None
    processed_date: Optional[datetime] = None


class PayrollResponse(PayrollBase):
    """Schema for payroll response."""
    id: int
    employee_id: int
    processed_date: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PayslipBase(BaseModel):
    """Base payslip schema."""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2100)


class PayslipResponse(PayslipBase):
    """Schema for payslip response."""
    id: int
    payroll_id: int
    employee_id: int
    file_path: Optional[str] = None
    generated_date: datetime
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True