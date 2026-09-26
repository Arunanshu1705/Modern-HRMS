from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time
from app.models.attendance import AttendanceStatus


class AttendanceBase(BaseModel):
    """Base attendance schema."""
    date: datetime
    check_in: time
    check_out: Optional[time] = None
    notes: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    """Schema for creating attendance record."""
    employee_id: int


class AttendanceUpdate(BaseModel):
    """Schema for updating attendance record."""
    check_out: Optional[time] = None
    status: Optional[AttendanceStatus] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response."""
    id: int
    employee_id: int
    working_hours: float
    status: AttendanceStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CheckInResponse(BaseModel):
    """Schema for check-in response."""
    message: str
    attendance: AttendanceResponse


class CheckOutResponse(BaseModel):
    """Schema for check-out response."""
    message: str
    attendance: AttendanceResponse
    working_hours: float


class AttendanceOverview(BaseModel):
    """Schema for attendance overview statistics."""
    total_employees: int
    present_today: int
    absent_today: int
    late_today: int
    on_leave_today: int
    average_working_hours: float


class AttendanceAnalytics(BaseModel):
    """Schema for attendance analytics."""
    employee_id: int
    employee_name: str
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    on_leave_days: int
    average_working_hours: float
    attendance_percentage: float