from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin for adding created_at and updated_at timestamps to models."""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class BaseModel(Base):
    """Base model with common fields."""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)