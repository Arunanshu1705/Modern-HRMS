from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, date
from app.models.leave import LeaveStatus


class LeaveTypeBase(BaseModel):
    """Base leave type schema."""
    name: str = Field(..., min_length=1, max_length=50)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    days_allowed: int = Field(..., ge=0)
    is_paid: bool = True


class LeaveTypeCreate(LeaveTypeBase):
    """Schema for creating leave type."""
    pass


class LeaveTypeResponse(LeaveTypeBase):
    """Schema for leave type response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LeaveBalanceBase(BaseModel):
    """Base leave balance schema."""
    employee_id: int
    leave_type_id: int
    year: int
    total_days: int = Field(..., ge=0)
    used_days: int = Field(..., ge=0)
    remaining_days: int = Field(..., ge=0)


class LeaveBalanceResponse(LeaveBalanceBase):
    """Schema for leave balance response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    leave_type_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class LeaveRequestBase(BaseModel):
    """Base leave request schema."""
    leave_type_id: int
    start_date: date
    end_date: date
    reason: str = Field(..., min_length=1)


class LeaveRequestCreate(LeaveRequestBase):
    """Schema for creating leave request."""
    pass


class LeaveRequestUpdate(BaseModel):
    """Schema for updating leave request (admin only)."""
    status: LeaveStatus
    rejection_reason: Optional[str] = None


class LeaveRequestResponse(LeaveRequestBase):
    """Schema for leave request response."""
    id: int
    employee_id: int
    total_days: int
    status: LeaveStatus
    approved_by: Optional[int] = None
    approved_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    employee_name: Optional[str] = None
    leave_type_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class LeaveRequestDetail(LeaveRequestResponse):
    """Schema for leave request with employee details."""
    employee_name: str
    employee_code: str
    department_name: Optional[str] = None
    
    class Config:
        from_attributes = True