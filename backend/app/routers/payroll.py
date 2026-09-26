from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.database.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.schemas.payroll import (
    SalaryDetailCreate, SalaryDetailUpdate, SalaryDetailResponse,
    PayrollCreate, PayrollUpdate, PayrollResponse,
    PayslipResponse
)
from app.models import SalaryDetail, Payroll, Payslip, Employee, User
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
import os

router = APIRouter()


# Salary Detail endpoints (admin only)
@router.post("/salary-details", response_model=SalaryDetailResponse)
async def create_salary_detail(
    salary_detail: SalaryDetailCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create salary details for an employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == salary_detail.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    new_salary_detail = SalaryDetail(**salary_detail.model_dump())
    db.add(new_salary_detail)
    db.commit()
    db.refresh(new_salary_detail)
    
    return new_salary_detail


@router.get("/salary-details/{employee_id}", response_model=SalaryDetailResponse)
async def get_salary_detail(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get salary details for an employee (admin only)."""
    salary_detail = db.query(SalaryDetail).filter(
        SalaryDetail.employee_id == employee_id
    ).order_by(SalaryDetail.effective_date.desc()).first()
    
    if not salary_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary details not found"
        )
    
    return salary_detail


@router.put("/salary-details/{employee_id}", response_model=SalaryDetailResponse)
async def update_salary_detail(
    employee_id: int,
    salary_update: SalaryDetailUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Update salary details for an employee (admin only)."""
    salary_detail = db.query(SalaryDetail).filter(
        SalaryDetail.employee_id == employee_id
    ).order_by(SalaryDetail.effective_date.desc()).first()
    
    if not salary_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Salary details not found"
        )
    
    for field, value in salary_update.model_dump(exclude_unset=True).items():
        setattr(salary_detail, field, value)
    
    db.commit()
    db.refresh(salary_detail)
    
    return salary_detail


# Payroll endpoints
@router.post("/", response_model=PayrollResponse)
async def create_payroll(
    payroll: PayrollCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Create payroll record (admin only)."""
    employee = db.query(Employee).filter(Employee.id == payroll.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Check if payroll already exists for this employee, month, year
    existing = db.query(Payroll).filter(
        Payroll.employee_id == payroll.employee_id,
        Payroll.month == payroll.month,
        Payroll.year == payroll.year
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payroll already exists for this employee, month, and year"
        )
    
    new_payroll = Payroll(**payroll.model_dump())
    db.add(new_payroll)
    db.commit()
    db.refresh(new_payroll)
    
    return new_payroll


@router.get("/me", response_model=List[PayrollResponse])
async def get_my_payroll(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's payroll history."""
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
    
    query = db.query(Payroll).filter(Payroll.employee_id == employee.id)
    
    if year:
        query = query.filter(Payroll.year == year)
    
    payroll_records = query.order_by(Payroll.year.desc(), Payroll.month.desc()).limit(24).all()
    return payroll_records


@router.get("/{employee_id}", response_model=List[PayrollResponse])
async def get_employee_payroll(
    employee_id: int,
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Get payroll history for a specific employee (admin only)."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    query = db.query(Payroll).filter(Payroll.employee_id == employee_id)
    
    if year:
        query = query.filter(Payroll.year == year)
    
    payroll_records = query.order_by(Payroll.year.desc(), Payroll.month.desc()).limit(24).all()
    return payroll_records


@router.put("/{payroll_id}", response_model=PayrollResponse)
async def update_payroll(
    payroll_id: int,
    payroll_update: PayrollUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Update payroll record (admin only)."""
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll record not found"
        )
    
    for field, value in payroll_update.model_dump(exclude_unset=True).items():
        setattr(payroll, field, value)
    
    db.commit()
    db.refresh(payroll)
    
    return payroll


# Payslip endpoints
@router.post("/payslips/{payroll_id}", response_model=PayslipResponse)
async def generate_payslip(
    payroll_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin)
):
    """Generate payslip PDF (admin only)."""
    payroll = db.query(Payroll).filter(Payroll.id == payroll_id).first()
    if not payroll:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payroll record not found"
        )
    
    employee = db.query(Employee).filter(Employee.id == payroll.employee_id).first()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )
    
    # Generate PDF
    filename = f"payslip_{employee.employee_code}_{payroll.month}_{payroll.year}.pdf"
    filepath = os.path.join("payslips", filename)
    
    # Create payslips directory if it doesn't exist
    os.makedirs("payslips", exist_ok=True)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = Paragraph(f"Payslip - {employee.first_name} {employee.last_name}", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Employee details
    employee_data = [
        ["Employee Code:", employee.employee_code],
        ["Employee Name:", f"{employee.first_name} {employee.last_name}"],
        ["Department:", employee.department.name if employee.department else "N/A"],
        ["Designation:", employee.designation or "N/A"],
        ["Period:", f"{payroll.month}/{payroll.year}"]
    ]
    
    employee_table = Table(employee_data, colWidths=[150, 300])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(employee_table)
    story.append(Spacer(1, 24))
    
    # Earnings
    earnings_title = Paragraph("Earnings", styles['Heading2'])
    story.append(earnings_title)
    
    earnings_data = [
        ["Description", "Amount"],
        ["Basic Salary", f"${payroll.basic_salary:,.2f}"],
        ["HRA", f"${payroll.hra:,.2f}"],
        ["DA", f"${payroll.da:,.2f}"],
        ["Transport Allowance", f"${payroll.transport_allowance:,.2f}"],
        ["Medical Allowance", f"${payroll.medical_allowance:,.2f}"],
        ["Other Allowances", f"${payroll.other_allowances:,.2f}"],
        ["Total Earnings", f"${payroll.total_earnings:,.2f}"]
    ]
    
    earnings_table = Table(earnings_data, colWidths=[200, 150])
    earnings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(earnings_table)
    story.append(Spacer(1, 24))
    
    # Deductions
    deductions_title = Paragraph("Deductions", styles['Heading2'])
    story.append(deductions_title)
    
    deductions_data = [
        ["Description", "Amount"],
        ["PF Deduction", f"${payroll.pf_deduction:,.2f}"],
        ["Tax Deduction", f"${payroll.tax_deduction:,.2f}"],
        ["Other Deductions", f"${payroll.other_deductions:,.2f}"],
        ["Total Deductions", f"${payroll.total_deductions:,.2f}"]
    ]
    
    deductions_table = Table(deductions_data, colWidths=[200, 150])
    deductions_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
    ]))
    
    story.append(deductions_table)
    story.append(Spacer(1, 24))
    
    # Net Salary
    net_salary_title = Paragraph("Net Salary", styles['Heading2'])
    story.append(net_salary_title)
    
    net_salary_data = [
        ["Net Salary", f"${payroll.net_salary:,.2f}"]
    ]
    
    net_salary_table = Table(net_salary_data, colWidths=[200, 150])
    net_salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(net_salary_table)
    
    # Build PDF
    doc.build(story)
    
    # Create payslip record
    new_payslip = Payslip(
        payroll_id=payroll_id,
        employee_id=employee.id,
        month=payroll.month,
        year=payroll.year,
        file_path=filepath,
        generated_date=datetime.utcnow()
    )
    
    db.add(new_payslip)
    db.commit()
    db.refresh(new_payslip)
    
    return new_payslip


@router.get("/payslips/{payslip_id}/download")
async def download_payslip(
    payslip_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Download payslip PDF."""
    payslip = db.query(Payslip).filter(Payslip.id == payslip_id).first()
    if not payslip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payslip not found"
        )
    
    # Check if user has access to this payslip
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    
    # Admin can access any payslip, employee can only access their own
    if current_user["role"] != "admin" and (not employee or employee.id != payslip.employee_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this payslip"
        )
    
    if not payslip.file_path or not os.path.exists(payslip.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payslip file not found"
        )
    
    return FileResponse(
        payslip.file_path,
        media_type="application/pdf",
        filename=os.path.basename(payslip.file_path)
    )


@router.get("/payslips/me", response_model=List[PayslipResponse])
async def get_my_payslips(
    year: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current employee's payslips."""
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
    
    query = db.query(Payslip).filter(Payslip.employee_id == employee.id)
    
    if year:
        query = query.filter(Payslip.year == year)
    
    payslips = query.order_by(Payslip.year.desc(), Payslip.month.desc()).limit(24).all()
    return payslips