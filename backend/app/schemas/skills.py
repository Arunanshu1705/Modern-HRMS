from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SkillBase(BaseModel):
    """Base skill schema."""
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    description: Optional[str] = None


class SkillCreate(SkillBase):
    """Schema for creating skill."""
    pass


class SkillResponse(SkillBase):
    """Schema for skill response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeSkillBase(BaseModel):
    """Base employee skill schema."""
    skill_id: int
    proficiency_level: int = Field(default=1, ge=1, le=5)
    years_of_experience: float = Field(default=0.0, ge=0)


class EmployeeSkillCreate(EmployeeSkillBase):
    """Schema for creating employee skill."""
    pass


class EmployeeSkillUpdate(BaseModel):
    """Schema for updating employee skill."""
    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    years_of_experience: Optional[float] = Field(None, ge=0)


class EmployeeSkillResponse(EmployeeSkillBase):
    """Schema for employee skill response."""
    id: int
    employee_id: int
    skill_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ToolBase(BaseModel):
    """Base tool schema."""
    name: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = None
    description: Optional[str] = None


class ToolCreate(ToolBase):
    """Schema for creating tool."""
    pass


class ToolResponse(ToolBase):
    """Schema for tool response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeToolBase(BaseModel):
    """Base employee tool schema."""
    tool_id: int
    proficiency_level: int = Field(default=1, ge=1, le=5)
    years_of_experience: float = Field(default=0.0, ge=0)


class EmployeeToolCreate(EmployeeToolBase):
    """Schema for creating employee tool."""
    pass


class EmployeeToolUpdate(BaseModel):
    """Schema for updating employee tool."""
    proficiency_level: Optional[int] = Field(None, ge=1, le=5)
    years_of_experience: Optional[float] = Field(None, ge=0)


class EmployeeToolResponse(EmployeeToolBase):
    """Schema for employee tool response."""
    id: int
    employee_id: int
    tool_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    client: Optional[str] = None
    technology_stack: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Schema for creating project."""
    pass


class ProjectResponse(ProjectBase):
    """Schema for project response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeProjectBase(BaseModel):
    """Base employee project schema."""
    project_id: int
    role: Optional[str] = None
    responsibilities: Optional[str] = None


class EmployeeProjectCreate(EmployeeProjectBase):
    """Schema for creating employee project."""
    pass


class EmployeeProjectResponse(EmployeeProjectBase):
    """Schema for employee project response."""
    id: int
    employee_id: int
    project_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WorkExperienceBase(BaseModel):
    """Base work experience schema."""
    company_name: str = Field(..., min_length=1, max_length=200)
    designation: str = Field(..., min_length=1, max_length=100)
    start_date: str = Field(..., min_length=1)
    end_date: Optional[str] = None
    description: Optional[str] = None


class WorkExperienceCreate(WorkExperienceBase):
    """Schema for creating work experience."""
    pass


class WorkExperienceResponse(WorkExperienceBase):
    """Schema for work experience response."""
    id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CertificationBase(BaseModel):
    """Base certification schema."""
    name: str = Field(..., min_length=1, max_length=200)
    issuing_organization: str = Field(..., min_length=1, max_length=200)
    issue_date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None
    verification_url: Optional[str] = None


class CertificationCreate(CertificationBase):
    """Schema for creating certification."""
    pass


class CertificationResponse(CertificationBase):
    """Schema for certification response."""
    id: int
    employee_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectRequirementBase(BaseModel):
    """Base project requirement schema."""
    project_id: int
    required_skill_id: Optional[int] = None
    required_tool_id: Optional[int] = None
    min_experience_years: float = Field(default=0.0, ge=0)
    proficiency_level: int = Field(default=1, ge=1, le=5)
    is_mandatory: bool = False


class ProjectRequirementCreate(ProjectRequirementBase):
    """Schema for creating project requirement."""
    pass


class ProjectRequirementResponse(ProjectRequirementBase):
    """Schema for project requirement response."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EmployeeMatch(BaseModel):
    """Schema for employee matching result."""
    employee_id: int
    employee_name: str
    employee_code: str
    designation: Optional[str] = None
    department_name: Optional[str] = None
    match_score: float
    matched_skills: list
    matched_tools: list
    total_experience: float