from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import BaseModel, TimestampMixin
import enum
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EMPLOYEE = "employee"
class User(BaseModel, TimestampMixin):
    """User model for authentication."""
    __tablename__ = "users"
    
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.EMPLOYEE, nullable=False)
    
    # Relationship to employee
    employee = relationship("Employee", back_populates="user", uselist=False)