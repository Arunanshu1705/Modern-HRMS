from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from app.models.employee import EmployeeStatus


class EmployeeBase(BaseModel):
    """Base employee schema."""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    role_id: Optional[int] = None
    status: EmployeeStatus = EmployeeStatus.ACTIVE
    join_date: date
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "USA"


class EmployeeCreate(EmployeeBase):
    """Schema for creating a new employee."""
    employee_code: str = Field(..., min_length=1, max_length=50)
    user_id: Optional[int] = None


class EmployeeUpdate(BaseModel):
    """Schema for updating an employee."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    designation: Optional[str] = None
    department_id: Optional[int] = None
    role_id: Optional[int] = None
    status: Optional[EmployeeStatus] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class EmployeeResponse(EmployeeBase):
    """Schema for employee response."""
    id: int
    employee_code: str
    user_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeProfile(EmployeeResponse):
    """Schema for employee profile with additional details."""
    department_name: Optional[str] = None
    role_name: Optional[str] = None
    
    class Config:
        from_attributes = True