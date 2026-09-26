from sqlalchemy import Column, Integer, String, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
class Skill(BaseModel, TimestampMixin):
    """Skill model for employee competencies."""
    __tablename__ = "skills"
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    description = Column(Text)
    # Relationships
    employee_skills = relationship("EmployeeSkill", back_populates="skill")
class EmployeeSkill(BaseModel, TimestampMixin):
    """Employee skill mapping with proficiency level."""
    __tablename__ = "employee_skills"
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    proficiency_level = Column(Integer, default=1)  # 1-5 scale
    years_of_experience = Column(Float, default=0.0)
    # Relationships
    employee = relationship("Employee", back_populates="employee_skills")
    skill = relationship("Skill", back_populates="employee_skills")
class Tool(BaseModel, TimestampMixin):
    """Tool model for software/tools proficiency."""
    __tablename__ = "tools"
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))
    description = Column(Text)
    # Relationships
    employee_tools = relationship("EmployeeTool", back_populates="tool")
class EmployeeTool(BaseModel, TimestampMixin):
    """Employee tool mapping with proficiency level."""
    __tablename__ = "employee_tools"
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    tool_id = Column(Integer, ForeignKey("tools.id"), nullable=False)
    proficiency_level = Column(Integer, default=1)  # 1-5 scale
    years_of_experience = Column(Float, default=0.0)
    # Relationships
    employee = relationship("Employee", back_populates="employee_tools")
    tool = relationship("Tool", back_populates="employee_tools")
class Project(BaseModel, TimestampMixin):
    """Project model for employee project history."""
    __tablename__ = "projects"
    name = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(String(50))
    end_date = Column(String(50))
    client = Column(String(200))
    technology_stack = Column(Text)
    # Relationships
    employee_projects = relationship("EmployeeProject", back_populates="project")
class EmployeeProject(BaseModel, TimestampMixin):
    """Employee project mapping with role."""
    __tablename__ = "employee_projects"
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    role = Column(String(100))
    responsibilities = Column(Text)
    # Relationships
    employee = relationship("Employee", back_populates="employee_projects")
    project = relationship("Project", back_populates="employee_projects")
class WorkExperience(BaseModel, TimestampMixin):
    """Work experience model for previous employment."""
    __tablename__ = "work_experience"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    company_name = Column(String(200), nullable=False)
    designation = Column(String(100), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50))
    description = Column(Text)
    
    # Relationships
    employee = relationship("Employee", back_populates="work_experiences")


class Certification(BaseModel, TimestampMixin):
    """Certification model for professional certifications."""
    __tablename__ = "certifications"
    
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    name = Column(String(200), nullable=False)
    issuing_organization = Column(String(200), nullable=False)
    issue_date = Column(String(50))
    expiry_date = Column(String(50))
    credential_id = Column(String(100))
    verification_url = Column(String(500))
    
    # Relationships
    employee = relationship("Employee", back_populates="certifications")


class ProjectRequirement(BaseModel, TimestampMixin):
    """Project requirement model for matching employees to projects."""
    __tablename__ = "project_requirements"
    
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    required_skill_id = Column(Integer, ForeignKey("skills.id"))
    required_tool_id = Column(Integer, ForeignKey("tools.id"))
    min_experience_years = Column(Float, default=0.0)
    proficiency_level = Column(Integer, default=1)
    is_mandatory = Column(Boolean, default=False)
    
    # Relationships
    project = relationship("Project")
    required_skill = relationship("Skill")
    required_tool = relationship("Tool")