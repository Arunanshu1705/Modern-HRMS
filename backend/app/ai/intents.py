from enum import Enum


class Intent(str, Enum):
    """AI Chatbot Intents for HRMS functionality."""
    
    # Navigation Intents
    NAVIGATE_ATTENDANCE = "navigate_attendance"
    NAVIGATE_LEAVE = "navigate_leave"
    NAVIGATE_PAYROLL = "navigate_payroll"
    NAVIGATE_CV_SKILLS = "navigate_cv_skills"
    NAVIGATE_ANNOUNCEMENTS = "navigate_announcements"
    NAVIGATE_HOLIDAYS = "navigate_holidays"
    NAVIGATE_EMPLOYEES = "navigate_employees"
    NAVIGATE_REPORTS = "navigate_reports"
    
    # Information Retrieval Intents (Employee)
    VIEW_ATTENDANCE = "view_attendance"
    VIEW_LEAVE_BALANCE = "view_leave_balance"
    VIEW_LEAVE_HISTORY = "view_leave_history"
    VIEW_SALARY = "view_salary"
    VIEW_PAYROLL = "view_payroll"
    VIEW_PAYSLIP = "view_payslip"
    VIEW_HOLIDAYS = "view_holidays"
    VIEW_ANNOUNCEMENTS = "view_announcements"
    
    # Action Intents (Employee)
    APPLY_LEAVE = "apply_leave"
    UPDATE_SKILLS = "update_skills"
    UPDATE_PROJECT = "update_project"
    UPDATE_CERTIFICATION = "update_certification"
    
    # Admin-Only Intents
    SEARCH_EMPLOYEES = "search_employees"
    VIEW_EMPLOYEE = "view_employee"
    APPROVE_LEAVE = "approve_leave"
    REJECT_LEAVE = "reject_leave"
    CREATE_ANNOUNCEMENT = "create_announcement"
    MANAGE_HOLIDAY = "manage_holiday"
    GENERATE_REPORT = "generate_report"
    
    # General Intents
    HELP = "help"
    UNKNOWN = "unknown"


INTENT_DESCRIPTIONS = {
    Intent.NAVIGATE_ATTENDANCE: "Navigate to Attendance Management section",
    Intent.NAVIGATE_LEAVE: "Navigate to Leave Management section",
    Intent.NAVIGATE_PAYROLL: "Navigate to Payroll Management section",
    Intent.NAVIGATE_CV_SKILLS: "Navigate to CV/Skills Database section",
    Intent.NAVIGATE_ANNOUNCEMENTS: "Navigate to Announcements section",
    Intent.NAVIGATE_HOLIDAYS: "Navigate to Holiday Calendar section",
    Intent.NAVIGATE_EMPLOYEES: "Navigate to Employee Management section (admin only)",
    Intent.NAVIGATE_REPORTS: "Navigate to Reports & Analytics section (admin only)",
    Intent.VIEW_ATTENDANCE: "View attendance records",
    Intent.VIEW_LEAVE_BALANCE: "View leave balance",
    Intent.VIEW_LEAVE_HISTORY: "View leave history",
    Intent.VIEW_SALARY: "View salary details",
    Intent.VIEW_PAYROLL: "View payroll history",
    Intent.VIEW_PAYSLIP: "View payslip",
    Intent.VIEW_HOLIDAYS: "View holidays",
    Intent.VIEW_ANNOUNCEMENTS: "View announcements",
    Intent.APPLY_LEAVE: "Apply for leave",
    Intent.UPDATE_SKILLS: "Update skills",
    Intent.UPDATE_PROJECT: "Update project information",
    Intent.UPDATE_CERTIFICATION: "Update certification",
    Intent.SEARCH_EMPLOYEES: "Search employees (admin only)",
    Intent.VIEW_EMPLOYEE: "View employee details (admin only)",
    Intent.APPROVE_LEAVE: "Approve leave request (admin only)",
    Intent.REJECT_LEAVE: "Reject leave request (admin only)",
    Intent.CREATE_ANNOUNCEMENT: "Create announcement (admin only)",
    Intent.MANAGE_HOLIDAY: "Manage holidays (admin only)",
    Intent.GENERATE_REPORT: "Generate reports (admin only)",
    Intent.HELP: "Get help and guidance",
    Intent.UNKNOWN: "Unknown intent"
}