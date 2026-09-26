from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app.database.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.skills import (
    SkillCreate, SkillResponse,
    EmployeeSkillCreate, EmployeeSkillUpdate, EmployeeSkillResponse,
    ToolCreate, ToolResponse,
    EmployeeToolCreate, EmployeeToolUpdate, EmployeeToolResponse,
    ProjectCreate, ProjectResponse,
    EmployeeProjectCreate, EmployeeProjectResponse,
    WorkExperienceCreate, WorkExperienceResponse,
    CertificationCreate, CertificationResponse,
    ProjectRequirementCreate, ProjectRequirementResponse,
    EmployeeMatch
)
from app.models import (
    Skill, EmployeeSkill, Tool, EmployeeTool,
    Project, EmployeeProject, WorkExperience,
    Certification, ProjectRequirement, Employee, User
)

router = APIRouter()


# Skill endpoints
@router.post("/skills", response_model=SkillResponse)
async def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new skill (admin only)."""
    existing = db.query(Skill).filter(Skill.name == skill.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already exists"
        )
    
    new_skill = Skill(**skill.model_dump())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    
    return new_skill


@router.get("/skills", response_model=List[SkillResponse])
async def get_skills(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all skills."""
    query = db.query(Skill).filter(Skill.is_active == True)
    
    if category:
        query = query.filter(Skill.category == category)
    
    skills = query.all()
    return skills


# Employee Skill endpoints
@router.post("/employee-skills", response_model=EmployeeSkillResponse)
async def create_employee_skill(
    employee_skill: EmployeeSkillCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a skill to employee's profile."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Check if skill exists
    skill = db.query(Skill).filter(Skill.id == employee_skill.skill_id).first()
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    
    # Check if employee already has this skill
    existing = db.query(EmployeeSkill).filter(
        and_(
            EmployeeSkill.employee_id == employee.id,
            EmployeeSkill.skill_id == employee_skill.skill_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already has this skill"
        )
    
    new_employee_skill = EmployeeSkill(
        employee_id=employee.id,
        **employee_skill.model_dump()
    )
    
    db.add(new_employee_skill)
    db.commit()
    db.refresh(new_employee_skill)
    
    # Add skill name
    new_employee_skill.skill_name = skill.name
    
    return new_employee_skill


@router.get("/employee-skills/me", response_model=List[EmployeeSkillResponse])
async def get_my_skills(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's skills."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    employee_skills = db.query(EmployeeSkill).filter(
        EmployeeSkill.employee_id == employee.id
    ).all()
    
    # Add skill names
    result = []
    for emp_skill in employee_skills:
        skill = db.query(Skill).filter(Skill.id == emp_skill.skill_id).first()
        emp_skill_dict = emp_skill.__dict__.copy()
        emp_skill_dict['skill_name'] = skill.name if skill else None
        result.append(EmployeeSkillResponse(**emp_skill_dict))
    
    return result


@router.put("/employee-skills/{skill_id}", response_model=EmployeeSkillResponse)
async def update_employee_skill(
    skill_id: int,
    skill_update: EmployeeSkillUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update employee's skill."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    employee_skill = db.query(EmployeeSkill).filter(
        and_(
            EmployeeSkill.employee_id == employee.id,
            EmployeeSkill.skill_id == skill_id
        )
    ).first()
    
    if not employee_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee skill not found"
        )
    
    for field, value in skill_update.model_dump(exclude_unset=True).items():
        setattr(employee_skill, field, value)
    
    db.commit()
    db.refresh(employee_skill)
    
    # Add skill name
    skill = db.query(Skill).filter(Skill.id == employee_skill.skill_id).first()
    employee_skill.skill_name = skill.name if skill else None
    
    return employee_skill


@router.delete("/employee-skills/{skill_id}")
async def delete_employee_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete employee's skill."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    employee_skill = db.query(EmployeeSkill).filter(
        and_(
            EmployeeSkill.employee_id == employee.id,
            EmployeeSkill.skill_id == skill_id
        )
    ).first()
    
    if not employee_skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee skill not found"
        )
    
    db.delete(employee_skill)
    db.commit()
    
    return {"message": "Skill deleted successfully"}


# Tool endpoints
@router.post("/tools", response_model=ToolResponse)
async def create_tool(
    tool: ToolCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new tool (admin only)."""
    existing = db.query(Tool).filter(Tool.name == tool.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tool already exists"
        )
    
    new_tool = Tool(**tool.model_dump())
    db.add(new_tool)
    db.commit()
    db.refresh(new_tool)
    
    return new_tool


@router.get("/tools", response_model=List[ToolResponse])
async def get_tools(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all tools."""
    query = db.query(Tool).filter(Tool.is_active == True)
    
    if category:
        query = query.filter(Tool.category == category)
    
    tools = query.all()
    return tools


# Employee Tool endpoints
@router.post("/employee-tools", response_model=EmployeeToolResponse)
async def create_employee_tool(
    employee_tool: EmployeeToolCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a tool to employee's profile."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Check if tool exists
    tool = db.query(Tool).filter(Tool.id == employee_tool.tool_id).first()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Check if employee already has this tool
    existing = db.query(EmployeeTool).filter(
        and_(
            EmployeeTool.employee_id == employee.id,
            EmployeeTool.tool_id == employee_tool.tool_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee already has this tool"
        )
    
    new_employee_tool = EmployeeTool(
        employee_id=employee.id,
        **employee_tool.model_dump()
    )
    
    db.add(new_employee_tool)
    db.commit()
    db.refresh(new_employee_tool)
    
    # Add tool name
    new_employee_tool.tool_name = tool.name
    
    return new_employee_tool


@router.get("/employee-tools/me", response_model=List[EmployeeToolResponse])
async def get_my_tools(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's tools."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    employee_tools = db.query(EmployeeTool).filter(
        EmployeeTool.employee_id == employee.id
    ).all()
    
    # Add tool names
    result = []
    for emp_tool in employee_tools:
        tool = db.query(Tool).filter(Tool.id == emp_tool.tool_id).first()
        emp_tool_dict = emp_tool.__dict__.copy()
        emp_tool_dict['tool_name'] = tool.name if tool else None
        result.append(EmployeeToolResponse(**emp_tool_dict))
    
    return result


# Project endpoints
@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create a new project (admin only)."""
    new_project = Project(**project.model_dump())
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    
    return new_project


@router.get("/projects", response_model=List[ProjectResponse])
async def get_projects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all projects."""
    projects = db.query(Project).filter(Project.is_active == True).all()
    return projects


# Employee Project endpoints
@router.post("/employee-projects", response_model=EmployeeProjectResponse)
async def create_employee_project(
    employee_project: EmployeeProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add a project to employee's profile."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    # Check if project exists
    project = db.query(Project).filter(Project.id == employee_project.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    new_employee_project = EmployeeProject(
        employee_id=employee.id,
        **employee_project.model_dump()
    )
    
    db.add(new_employee_project)
    db.commit()
    db.refresh(new_employee_project)
    
    # Add project name
    new_employee_project.project_name = project.name
    
    return new_employee_project


@router.get("/employee-projects/me", response_model=List[EmployeeProjectResponse])
async def get_my_projects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's projects."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    employee_projects = db.query(EmployeeProject).filter(
        EmployeeProject.employee_id == employee.id
    ).all()
    
    # Add project names
    result = []
    for emp_project in employee_projects:
        project = db.query(Project).filter(Project.id == emp_project.project_id).first()
        emp_project_dict = emp_project.__dict__.copy()
        emp_project_dict['project_name'] = project.name if project else None
        result.append(EmployeeProjectResponse(**emp_project_dict))
    
    return result


# Work Experience endpoints
@router.post("/work-experience", response_model=WorkExperienceResponse)
async def create_work_experience(
    work_experience: WorkExperienceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add work experience to employee's profile."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    new_work_experience = WorkExperience(
        employee_id=employee.id,
        **work_experience.model_dump()
    )
    
    db.add(new_work_experience)
    db.commit()
    db.refresh(new_work_experience)
    
    return new_work_experience


@router.get("/work-experience/me", response_model=List[WorkExperienceResponse])
async def get_my_work_experience(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's work experience."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    work_experiences = db.query(WorkExperience).filter(
        WorkExperience.employee_id == employee.id
    ).order_by(WorkExperience.start_date.desc()).all()
    
    return work_experiences


# Certification endpoints
@router.post("/certifications", response_model=CertificationResponse)
async def create_certification(
    certification: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add certification to employee's profile."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    new_certification = Certification(
        employee_id=employee.id,
        **certification.model_dump()
    )
    
    db.add(new_certification)
    db.commit()
    db.refresh(new_certification)
    
    return new_certification


@router.get("/certifications/me", response_model=List[CertificationResponse])
async def get_my_certifications(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's certifications."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee profile not found"
        )
    
    certifications = db.query(Certification).filter(
        Certification.employee_id == employee.id
    ).order_by(Certification.issue_date.desc()).all()
    
    return certifications


# Project Requirement endpoints (admin only)
@router.post("/project-requirements", response_model=ProjectRequirementResponse)
async def create_project_requirement(
    requirement: ProjectRequirementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create project requirement (admin only)."""
    new_requirement = ProjectRequirement(**requirement.model_dump())
    db.add(new_requirement)
    db.commit()
    db.refresh(new_requirement)
    
    return new_requirement


@router.post("/employees/match", response_model=List[EmployeeMatch])
async def match_employees(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Match employees to project requirements (admin only)."""
    # Get project requirements
    requirements = db.query(ProjectRequirement).filter(
        ProjectRequirement.project_id == project_id
    ).all()
    
    if not requirements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No requirements found for this project"
        )
    
    # Get all active employees
    employees = db.query(Employee).filter(Employee.is_active == True).all()
    
    matches = []
    for employee in employees:
        match_score = 0.0
        matched_skills = []
        matched_tools = []
        total_experience = 0.0
        
        # Calculate total experience from work history
        work_experiences = db.query(WorkExperience).filter(
            WorkExperience.employee_id == employee.id
        ).all()
        
        for exp in work_experiences:
            if exp.end_date:
                # Calculate years of experience
                try:
                    start = datetime.strptime(exp.start_date, "%Y-%m-%d")
                    end = datetime.strptime(exp.end_date, "%Y-%m-%d")
                    years = (end - start).days / 365.25
                    total_experience += years
                except:
                    pass
        
        # Check skill matches
        for req in requirements:
            if req.required_skill_id:
                employee_skill = db.query(EmployeeSkill).filter(
                    and_(
                        EmployeeSkill.employee_id == employee.id,
                        EmployeeSkill.skill_id == req.required_skill_id
                    )
                ).first()
                
                if employee_skill:
                    skill = db.query(Skill).filter(Skill.id == req.required_skill_id).first()
                    if skill:
                        matched_skills.append(skill.name)
                        # Score based on proficiency level
                        if employee_skill.proficiency_level >= req.proficiency_level:
                            match_score += 20 if req.is_mandatory else 10
                        else:
                            match_score += 10 if req.is_mandatory else 5
        
        # Check tool matches
        for req in requirements:
            if req.required_tool_id:
                employee_tool = db.query(EmployeeTool).filter(
                    and_(
                        EmployeeTool.employee_id == employee.id,
                        EmployeeTool.tool_id == req.required_tool_id
                    )
                ).first()
                
                if employee_tool:
                    tool = db.query(Tool).filter(Tool.id == req.required_tool_id).first()
                    if tool:
                        matched_tools.append(tool.name)
                        # Score based on proficiency level
                        if employee_tool.proficiency_level >= req.proficiency_level:
                            match_score += 15 if req.is_mandatory else 8
                        else:
                            match_score += 8 if req.is_mandatory else 4
        
        # Normalize score to 0-100
        match_score = min(match_score, 100.0)
        
        # Get department name
        department_name = None
        if employee.department:
            department_name = employee.department.name
        
        matches.append(EmployeeMatch(
            employee_id=employee.id,
            employee_name=f"{employee.first_name} {employee.last_name}",
            employee_code=employee.employee_code,
            designation=employee.designation,
            department_name=department_name,
            match_score=match_score,
            matched_skills=matched_skills,
            matched_tools=matched_tools,
            total_experience=round(total_experience, 2)
        ))
    
    # Sort by match score
    matches.sort(key=lambda x: x.match_score, reverse=True)
    
    return matches
