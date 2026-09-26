from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.company import (
    AnnouncementCreate, AnnouncementUpdate, AnnouncementResponse,
    HolidayCreate, HolidayUpdate, HolidayResponse
)
from app.models import Announcement, Holiday, Employee, User

router = APIRouter()


# Announcement endpoints
@router.post("/announcements", response_model=AnnouncementResponse)
async def create_announcement(
    announcement: AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new announcement (admin only)."""
    # Get current admin employee
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    admin_employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    
    new_announcement = Announcement(
        **announcement.model_dump(),
        published_date=datetime.utcnow(),
        author_id=admin_employee.id if admin_employee else None
    )
    
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    
    # Add author name
    if admin_employee:
        new_announcement.author_name = f"{admin_employee.first_name} {admin_employee.last_name}"
    
    return new_announcement


@router.get("/announcements", response_model=List[AnnouncementResponse])
async def get_announcements(
    priority_filter: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get announcements."""
    query = db.query(Announcement)
    
    if active_only:
        query = query.filter(Announcement.is_active == True)
        # Filter out expired announcements
        query = query.filter(
            (Announcement.expiry_date.is_(None)) | (Announcement.expiry_date > datetime.utcnow())
        )
    
    if priority_filter:
        query = query.filter(Announcement.priority == priority_filter)
    
    announcements = query.order_by(Announcement.published_date.desc()).limit(50).all()
    
    # Add author names
    result = []
    for announcement in announcements:
        announcement_dict = announcement.__dict__.copy()
        if announcement.author_id:
            author = db.query(Employee).filter(Employee.id == announcement.author_id).first()
            announcement_dict['author_name'] = f"{author.first_name} {author.last_name}" if author else None
        result.append(AnnouncementResponse(**announcement_dict))
    
    return result


@router.get("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def get_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific announcement."""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    # Add author name
    if announcement.author_id:
        author = db.query(Employee).filter(Employee.id == announcement.author_id).first()
        announcement.author_name = f"{author.first_name} {author.last_name}" if author else None
    
    return announcement


@router.put("/announcements/{announcement_id}", response_model=AnnouncementResponse)
async def update_announcement(
    announcement_id: int,
    announcement_update: AnnouncementUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Update an announcement (admin only)."""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    for field, value in announcement_update.model_dump(exclude_unset=True).items():
        setattr(announcement, field, value)
    
    db.commit()
    db.refresh(announcement)
    
    # Add author name
    if announcement.author_id:
        author = db.query(Employee).filter(Employee.id == announcement.author_id).first()
        announcement.author_name = f"{author.first_name} {author.last_name}" if author else None
    
    return announcement


@router.delete("/announcements/{announcement_id}")
async def delete_announcement(
    announcement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Delete an announcement (admin only)."""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    announcement.is_active = False
    db.commit()
    
    return {"message": "Announcement deleted successfully"}


# Holiday endpoints
@router.post("/holidays", response_model=HolidayResponse)
async def create_holiday(
    holiday: HolidayCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new holiday (admin only)."""
    # Check if holiday already exists for this date
    existing = db.query(Holiday).filter(Holiday.date == holiday.date).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Holiday already exists for this date"
        )
    
    new_holiday = Holiday(**holiday.model_dump())
    db.add(new_holiday)
    db.commit()
    db.refresh(new_holiday)
    
    return new_holiday


@router.get("/holidays", response_model=List[HolidayResponse])
async def get_holidays(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get holidays."""
    query = db.query(Holiday).filter(Holiday.is_active == True)
    
    if year:
        from sqlalchemy import extract
        query = query.filter(extract('year', Holiday.date) == year)
    
    holidays = query.order_by(Holiday.date.asc()).all()
    return holidays


@router.get("/holidays/upcoming", response_model=List[HolidayResponse])
async def get_upcoming_holidays(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get upcoming holidays."""
    from datetime import timedelta
    today = datetime.now().date()
    one_year_later = today + timedelta(days=365)
    
    holidays = db.query(Holiday).filter(
        Holiday.is_active == True,
        Holiday.date >= today,
        Holiday.date <= one_year_later
    ).order_by(Holiday.date.asc()).limit(limit).all()
    
    return holidays


@router.put("/holidays/{holiday_id}", response_model=HolidayResponse)
async def update_holiday(
    holiday_id: int,
    holiday_update: HolidayUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Update a holiday (admin only)."""
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )
    
    for field, value in holiday_update.model_dump(exclude_unset=True).items():
        setattr(holiday, field, value)
    
    db.commit()
    db.refresh(holiday)
    
    return holiday


@router.delete("/holidays/{holiday_id}")
async def delete_holiday(
    holiday_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Delete a holiday (admin only)."""
    holiday = db.query(Holiday).filter(Holiday.id == holiday_id).first()
    if not holiday:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holiday not found"
        )
    
    holiday.is_active = False
    db.commit()
    
    return {"message": "Holiday deleted successfully"}