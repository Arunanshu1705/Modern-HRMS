from app.ai.intents import Intent


# Define which intents are accessible by which roles
ROLE_PERMISSIONS = {
    "employee": [
        # Navigation
        Intent.NAVIGATE_ATTENDANCE,
        Intent.NAVIGATE_LEAVE,
        Intent.NAVIGATE_PAYROLL,
        Intent.NAVIGATE_CV_SKILLS,
        Intent.NAVIGATE_ANNOUNCEMENTS,
        Intent.NAVIGATE_HOLIDAYS,
        
        # Information Retrieval
        Intent.VIEW_ATTENDANCE,
        Intent.VIEW_LEAVE_BALANCE,
        Intent.VIEW_LEAVE_HISTORY,
        Intent.VIEW_SALARY,
        Intent.VIEW_PAYROLL,
        Intent.VIEW_PAYSLIP,
        Intent.VIEW_HOLIDAYS,
        Intent.VIEW_ANNOUNCEMENTS,
        
        # Actions
        Intent.APPLY_LEAVE,
        Intent.UPDATE_SKILLS,
        Intent.UPDATE_PROJECT,
        Intent.UPDATE_CERTIFICATION,
        
        # General
        Intent.HELP,
        Intent.UNKNOWN
    ],
    "admin": [
        # All employee permissions
        "employee",  # Inherits all employee permissions
        
        # Admin-specific navigation
        Intent.NAVIGATE_EMPLOYEES,
        Intent.NAVIGATE_REPORTS,
        
        # Admin-specific actions
        Intent.SEARCH_EMPLOYEES,
        Intent.VIEW_EMPLOYEE,
        Intent.APPROVE_LEAVE,
        Intent.REJECT_LEAVE,
        Intent.CREATE_ANNOUNCEMENT,
        Intent.MANAGE_HOLIDAY,
        Intent.GENERATE_REPORT,
        
        # General
        Intent.HELP,
        Intent.UNKNOWN
    ]
}


def has_permission(user_role: str, intent: Intent) -> bool:
    """Check if a user role has permission for a specific intent."""
    if user_role not in ROLE_PERMISSIONS:
        return False
    
    permissions = ROLE_PERMISSIONS[user_role]
    
    # Handle inheritance
    if isinstance(permissions, list) and "employee" in permissions and user_role == "admin":
        # Admin inherits employee permissions
        return True
    
    return intent in permissions


def get_allowed_intents(user_role: str) -> list:
    """Get all allowed intents for a user role."""
    if user_role not in ROLE_PERMISSIONS:
        return []
    
    permissions = ROLE_PERMISSIONS[user_role]
    
    # Handle inheritance for admin
    if user_role == "admin" and "employee" in permissions:
        # Admin gets all intents
        return [intent for intent in Intent if intent != Intent.UNKNOWN]
    
    return permissions if isinstance(permissions, list) else []