"""
Seed data script for PeopleHub HRMS.
Run this script to populate the database with initial sample data.
"""
from datetime import datetime, date, timedelta, time
from app.database.database import SessionLocal, init_db
from app.models import (
    User, UserRole, Employee, EmployeeStatus,
    Department, Role, LeaveType, LeaveBalance, LeaveRequest, LeaveStatus,
    Attendance, AttendanceStatus, SalaryDetail, Payroll, Payslip, PaymentStatus,
    Skill, EmployeeSkill, Tool, EmployeeTool, Project, EmployeeProject,
    WorkExperience, Certification, Announcement, AnnouncementPriority, Holiday
)
from app.core.security import get_password_hash


def seed_database():
    """Seed the database with sample data."""
    db = SessionLocal()
    
    try:
        print("Starting database seeding...")
        
        # Create departments
        print("Creating departments...")
        departments = [
            Department(name="Engineering", code="ENG", description="Software Engineering Department"),
            Department(name="Human Resources", code="HR", description="Human Resources Department"),
            Department(name="Finance", code="FIN", description="Finance Department"),
            Department(name="Marketing", code="MKT", description="Marketing Department"),
            Department(name="Operations", code="OPS", description="Operations Department")
        ]
        
        for dept in departments:
            db.add(dept)
        db.commit()
        
        # Create roles
        print("Creating roles...")
        roles = [
            Role(name="Software Engineer", description="Develops software applications"),
            Role(name="Senior Software Engineer", description="Senior developer role"),
            Role(name="HR Manager", description="Human Resources Manager"),
            Role(name="Finance Manager", description="Finance Manager"),
            Role(name="Marketing Manager", description="Marketing Manager"),
            Role(name="Operations Manager", description="Operations Manager")
        ]
        
        for role in roles:
            db.add(role)
        db.commit()
        
        # Refresh to get IDs
        db.refresh(departments[0])
        db.refresh(roles[0])
        
        # Create users and employees
        print("Creating users and employees...")
        
        # Admin user
        admin_user = User(
            user_id="admin",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        admin_employee = Employee(
            user_id=admin_user.id,
            first_name="Admin",
            last_name="User",
            email="admin@peoplehub.com",
            phone="555-0100",
            employee_code="EMP001",
            designation="System Administrator",
            department_id=departments[1].id,  # HR
            role_id=roles[2].id,  # HR Manager
            status=EmployeeStatus.ACTIVE,
            join_date=date(2020, 1, 1),
            address="123 Admin Street",
            city="Admin City",
            state="Admin State",
            postal_code="12345",
            country="USA"
        )
        db.add(admin_employee)
        db.commit()
        
        # Employee users
        employee_data = [
            {
                "user_id": "john.doe",
                "password": "password123",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@peoplehub.com",
                "phone": "555-0101",
                "employee_code": "EMP002",
                "designation": "Software Engineer",
                "department": "Engineering",
                "role": "Software Engineer",
                "join_date": date(2021, 3, 15)
            },
            {
                "user_id": "jane.smith",
                "password": "password123",
                "first_name": "Jane",
                "last_name": "Smith",
                "email": "jane.smith@peoplehub.com",
                "phone": "555-0102",
                "employee_code": "EMP003",
                "designation": "Senior Software Engineer",
                "department": "Engineering",
                "role": "Senior Software Engineer",
                "join_date": date(2020, 6, 1)
            },
            {
                "user_id": "bob.johnson",
                "password": "password123",
                "first_name": "Bob",
                "last_name": "Johnson",
                "email": "bob.johnson@peoplehub.com",
                "phone": "555-0103",
                "employee_code": "EMP004",
                "designation": "HR Manager",
                "department": "Human Resources",
                "role": "HR Manager",
                "join_date": date(2019, 8, 20)
            },
            {
                "user_id": "alice.williams",
                "password": "password123",
                "first_name": "Alice",
                "last_name": "Williams",
                "email": "alice.williams@peoplehub.com",
                "phone": "555-0104",
                "employee_code": "EMP005",
                "designation": "Finance Manager",
                "department": "Finance",
                "role": "Finance Manager",
                "join_date": date(2019, 2, 10)
            },
            {
                "user_id": "charlie.brown",
                "password": "password123",
                "first_name": "Charlie",
                "last_name": "Brown",
                "email": "charlie.brown@peoplehub.com",
                "phone": "555-0105",
                "employee_code": "EMP006",
                "designation": "Marketing Manager",
                "department": "Marketing",
                "role": "Marketing Manager",
                "join_date": date(2020, 11, 5)
            }
        ]
        
        employees = []
        for emp_data in employee_data:
            # Create user
            user = User(
                user_id=emp_data["user_id"],
                password_hash=get_password_hash(emp_data["password"]),
                role=UserRole.EMPLOYEE
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Find department and role
            dept = next((d for d in departments if d.name == emp_data["department"]), departments[0])
            role = next((r for r in roles if r.name == emp_data["role"]), roles[0])
            
            # Create employee
            employee = Employee(
                user_id=user.id,
                first_name=emp_data["first_name"],
                last_name=emp_data["last_name"],
                email=emp_data["email"],
                phone=emp_data["phone"],
                employee_code=emp_data["employee_code"],
                designation=emp_data["designation"],
                department_id=dept.id,
                role_id=role.id,
                status=EmployeeStatus.ACTIVE,
                join_date=emp_data["join_date"],
                address=f"{emp_data['first_name']}'s Address",
                city="Sample City",
                state="Sample State",
                postal_code="12345",
                country="USA"
            )
            db.add(employee)
            db.commit()
            db.refresh(employee)
            employees.append(employee)
        
        # Create leave types
        print("Creating leave types...")
        leave_types = [
            LeaveType(name="Annual Leave", code="AL", description="Annual vacation leave", days_allowed=20, is_paid=True),
            LeaveType(name="Sick Leave", code="SL", description="Sick leave", days_allowed=10, is_paid=True),
            LeaveType(name="Casual Leave", code="CL", description="Casual leave", days_allowed=5, is_paid=True),
            LeaveType(name="Comp-Off", code="CO", description="Compensatory off", days_allowed=0, is_paid=True)
        ]
        
        for lt in leave_types:
            db.add(lt)
        db.commit()
        db.refresh(leave_types[0])
        
        # Create leave balances for employees
        print("Creating leave balances...")
        current_year = datetime.now().year
        
        for employee in employees:
            for leave_type in leave_types:
                if leave_type.days_allowed > 0:
                    leave_balance = LeaveBalance(
                        employee_id=employee.id,
                        leave_type_id=leave_type.id,
                        year=current_year,
                        total_days=leave_type.days_allowed,
                        used_days=0,
                        remaining_days=leave_type.days_allowed
                    )
                    db.add(leave_balance)
        db.commit()
        
        # Create sample attendance records
        print("Creating attendance records...")
        today = date.today()
        
        for employee in employees:
            for i in range(30):  # Last 30 days
                attendance_date = today - timedelta(days=i)
                
                # Skip weekends
                if attendance_date.weekday() >= 5:
                    continue
                
                import random
                check_in_time = time(8, random.randint(0, 59)) if random.random() > 0.2 else time(9, random.randint(0, 59))
                check_out_time = time(17, random.randint(0, 59))
                
                status = AttendanceStatus.PRESENT if check_in_time < time(9, 0) else AttendanceStatus.LATE
                
                attendance = Attendance(
                    employee_id=employee.id,
                    date=datetime.combine(attendance_date, check_in_time),
                    check_in=check_in_time,
                    check_out=check_out_time,
                    working_hours=8.0 + random.uniform(-0.5, 0.5),
                    status=status
                )
                db.add(attendance)
        db.commit()
        
        # Create sample leave requests
        print("Creating leave requests...")
        sample_leave_request = LeaveRequest(
            employee_id=employees[0].id,
            leave_type_id=leave_types[0].id,  # Annual Leave
            start_date=today + timedelta(days=7),
            end_date=today + timedelta(days=10),
            total_days=4,
            reason="Family vacation",
            status=LeaveStatus.PENDING
        )
        db.add(sample_leave_request)
        db.commit()
        
        # Create salary details
        print("Creating salary details...")
        for employee in employees:
            salary_detail = SalaryDetail(
                employee_id=employee.id,
                basic_salary=50000.0,
                hra=10000.0,
                da=5000.0,
                transport_allowance=2000.0,
                medical_allowance=1500.0,
                other_allowances=1000.0,
                pf_deduction=6000.0,
                tax_deduction=8000.0,
                other_deductions=500.0,
                effective_date=date(2023, 1, 1)
            )
            db.add(salary_detail)
        db.commit()
        
        # Create sample payroll
        print("Creating payroll records...")
        for employee in employees:
            salary_detail = db.query(SalaryDetail).filter(SalaryDetail.employee_id == employee.id).first()
            if salary_detail:
                total_earnings = (salary_detail.basic_salary + salary_detail.hra + salary_detail.da +
                                salary_detail.transport_allowance + salary_detail.medical_allowance +
                                salary_detail.other_allowances)
                total_deductions = (salary_detail.pf_deduction + salary_detail.tax_deduction +
                                   salary_detail.other_deductions)
                
                payroll = Payroll(
                    employee_id=employee.id,
                    month=today.month,
                    year=today.year,
                    basic_salary=salary_detail.basic_salary,
                    hra=salary_detail.hra,
                    da=salary_detail.da,
                    transport_allowance=salary_detail.transport_allowance,
                    medical_allowance=salary_detail.medical_allowance,
                    other_allowances=salary_detail.other_allowances,
                    total_earnings=total_earnings,
                    pf_deduction=salary_detail.pf_deduction,
                    tax_deduction=salary_detail.tax_deduction,
                    other_deductions=salary_detail.other_deductions,
                    total_deductions=total_deductions,
                    net_salary=total_earnings - total_deductions,
                    days_present=22,
                    days_absent=0,
                    status=PaymentStatus.PROCESSED,
                    processed_date=datetime.utcnow()
                )
                db.add(payroll)
        db.commit()
        
        # Create skills
        print("Creating skills...")
        skills = [
            Skill(name="Python", category="Programming", description="Python programming language"),
            Skill(name="JavaScript", category="Programming", description="JavaScript programming language"),
            Skill(name="SQL", category="Database", description="SQL database queries"),
            Skill(name="Machine Learning", category="Data Science", description="Machine learning algorithms"),
            Skill(name="Project Management", category="Management", description="Project management skills")
        ]
        
        for skill in skills:
            db.add(skill)
        db.commit()
        
        # Create tools
        print("Creating tools...")
        tools = [
            Tool(name="Git", category="Version Control", description="Git version control system"),
            Tool(name="Docker", category="DevOps", description="Docker containerization"),
            Tool(name="AWS", category="Cloud", description="Amazon Web Services"),
            Tool(name="Excel", category="Office", description="Microsoft Excel"),
            Tool(name="Jira", category="Project Management", description="Jira project management")
        ]
        
        for tool in tools:
            db.add(tool)
        db.commit()
        
        # Create employee skills
        print("Creating employee skills...")
        for i, employee in enumerate(employees):
            # Assign some skills to employees
            skill_assignments = [
                (0, 4),  # Python, high proficiency
                (1, 3),  # JavaScript, medium proficiency
                (2, 4),  # SQL, high proficiency
                (3, 2),  # Machine Learning, low proficiency
            ]
            
            for skill_idx, proficiency in skill_assignments:
                if skill_idx < len(skills):
                    employee_skill = EmployeeSkill(
                        employee_id=employee.id,
                        skill_id=skills[skill_idx].id,
                        proficiency_level=proficiency,
                        years_of_experience=random.uniform(1, 5)
                    )
                    db.add(employee_skill)
        db.commit()
        
        # Create announcements
        print("Creating announcements...")
        announcements = [
            Announcement(
                title="Annual Company Meeting",
                content="Join us for our annual company meeting on December 15th at 2 PM in the main conference room.",
                priority=AnnouncementPriority.HIGH,
                published_date=datetime.utcnow(),
                author_id=admin_employee.id,
                expiry_date=datetime.utcnow() + timedelta(days=30)
            ),
            Announcement(
                title="New Holiday Schedule",
                content="The holiday schedule for 2024 has been updated. Please check the holiday calendar for details.",
                priority=AnnouncementPriority.MEDIUM,
                published_date=datetime.utcnow(),
                author_id=admin_employee.id,
                expiry_date=datetime.utcnow() + timedelta(days=60)
            ),
            Announcement(
                title="System Maintenance",
                content="Scheduled system maintenance will occur this weekend from Saturday 10 PM to Sunday 6 AM.",
                priority=AnnouncementPriority.URGENT,
                published_date=datetime.utcnow(),
                author_id=admin_employee.id,
                expiry_date=datetime.utcnow() + timedelta(days=7)
            )
        ]
        
        for announcement in announcements:
            db.add(announcement)
        db.commit()
        
        # Create holidays
        print("Creating holidays...")
        holidays = [
            Holiday(name="New Year's Day", date=date(today.year, 1, 1), holiday_type="National", description="New Year celebration", is_recurring=True),
            Holiday(name="Independence Day", date=date(today.year, 7, 4), holiday_type="National", description="Independence Day celebration", is_recurring=True),
            Holiday(name="Thanksgiving", date=date(today.year, 11, 28), holiday_type="National", description="Thanksgiving celebration", is_recurring=True),
            Holiday(name="Christmas", date=date(today.year, 12, 25), holiday_type="National", description="Christmas celebration", is_recurring=True),
            Holiday(name="Company Anniversary", date=date(today.year, 6, 15), holiday_type="Company", description="Company founding anniversary", is_recurring=True)
        ]
        
        for holiday in holidays:
            db.add(holiday)
        db.commit()
        
        print("Database seeding completed successfully!")
        print("\nSample credentials:")
        print("Admin - User ID: admin, Password: admin123")
        print("Employee - User ID: john.doe, Password: password123")
        print("Employee - User ID: jane.smith, Password: password123")
        print("Employee - User ID: bob.johnson, Password: password123")
        print("Employee - User ID: alice.williams, Password: password123")
        print("Employee - User ID: charlie.brown, Password: password123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database tables
    print("Initializing database...")
    init_db()
    
    # Seed data
    seed_database()