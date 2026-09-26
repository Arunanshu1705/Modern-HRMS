from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class LoginRequest(BaseModel):
    """Schema for login request."""
    user_id: str = Field(..., description="User ID for login")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """Schema for login response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: UserRole
    employee_id: Optional[int] = None


class TokenData(BaseModel):
    """Schema for token data."""
    user_id: Optional[str] = None
    role: Optional[str] = None


class UserBase(BaseModel):
    """Base user schema."""
    user_id: str
    role: UserRole


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True