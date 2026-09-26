from sqlalchemy import Column, Integer, ForeignKey, DateTime, Time, Float, Enum, String
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
import enum


class AttendanceStatus(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"


class Attendance(BaseModel, TimestampMixin):
    """Attendance model for tracking employee check-in/check-out."""
    __tablename__ = "attendance"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    check_in = Column(Time, nullable=False)
    check_out = Column(Time)
    working_hours = Column(Float, default=0.0)
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.PRESENT, nullable=False)
    notes = Column(String(500))
    
    # Relationships
    employee = relationship("Employee", back_populates="attendance_records")