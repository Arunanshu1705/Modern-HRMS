from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
from app.models.company import AnnouncementPriority


class AnnouncementBase(BaseModel):
    """Base announcement schema."""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    priority: AnnouncementPriority = AnnouncementPriority.MEDIUM
    expiry_date: Optional[datetime] = None


class AnnouncementCreate(AnnouncementBase):
    """Schema for creating announcement."""
    pass


class AnnouncementUpdate(BaseModel):
    """Schema for updating announcement."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    priority: Optional[AnnouncementPriority] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    """Schema for announcement response."""
    id: int
    published_date: datetime
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class HolidayBase(BaseModel):
    """Base holiday schema."""
    name: str = Field(..., min_length=1, max_length=200)
    date: date
    holiday_type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    is_recurring: bool = False


class HolidayCreate(HolidayBase):
    """Schema for creating holiday."""
    pass


class HolidayUpdate(BaseModel):
    """Schema for updating holiday."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    date: Optional[date] = None
    holiday_type: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    is_recurring: Optional[bool] = None


class HolidayResponse(HolidayBase):
    """Schema for holiday response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True