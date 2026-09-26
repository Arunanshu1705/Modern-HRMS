from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
class Department(BaseModel, TimestampMixin):
    """Department model for organizational structure."""
    __tablename__ = "departments"
    
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    employees = relationship("Employee", back_populates="department")
class Role(BaseModel, TimestampMixin):
    """Role model for job positions."""
    __tablename__ = "roles"
    
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    
    # Relationships
    employees = relationship("Employee", back_populates="role")