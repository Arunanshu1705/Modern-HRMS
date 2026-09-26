from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
import enum


class AnnouncementPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
class Announcement(BaseModel, TimestampMixin):
    """Announcement model for company updates and news."""
    __tablename__ = "announcements"
    
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Enum(AnnouncementPriority), default=AnnouncementPriority.MEDIUM, nullable=False)
    published_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    author_id = Column(Integer, ForeignKey("employees.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    author = relationship("Employee")


class Holiday(BaseModel, TimestampMixin):
    """Holiday model for company holidays."""
    __tablename__ = "holidays"
    
    name = Column(String(200), nullable=False)
    date = Column(Date, nullable=False, index=True)
    holiday_type = Column(String(50), nullable=False)  # National, Religious, Company
    description = Column(Text)
    is_recurring = Column(Boolean, default=False, nullable=False)