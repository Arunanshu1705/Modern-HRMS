from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    """Base department schema."""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None


class DepartmentCreate(DepartmentBase):
    """Schema for creating department."""
    pass


class DepartmentUpdate(BaseModel):
    """Schema for updating department."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None


class DepartmentResponse(DepartmentBase):
    """Schema for department response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    """Base role schema."""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating role."""
    pass


class RoleUpdate(BaseModel):
    """Schema for updating role."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True