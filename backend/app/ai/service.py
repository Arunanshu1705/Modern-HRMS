from typing import Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.ai.intents import Intent, INTENT_DESCRIPTIONS
from app.ai.prompts import SYSTEM_PROMPT, INTENT_DETECTION_PROMPT, RESPONSE_GENERATION_PROMPT
from app.ai.permissions import has_permission, get_allowed_intents
from app.ai.tools import HRMSTools
import re


class AIChatbotService:
    """AI Chatbot service for PeopleHub HRMS."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.system_prompt = SYSTEM_PROMPT
    
    def _detect_intent(self, user_message: str, user_role: str) -> Intent:
        """Detect the user's intent from their message."""
        if not self.client:
            # Fallback to simple keyword matching if OpenAI is not available
            return self._keyword_intent_detection(user_message, user_role)
        
        try:
            prompt = INTENT_DETECTION_PROMPT.format(
                user_message=user_message,
                user_role=user_role
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an intent detection system for an HRMS chatbot."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=50
            )
            
            intent_str = response.choices[0].message.content.strip().lower()
            
            # Map the detected intent string to Intent enum
            for intent in Intent:
                if intent.value == intent_str:
                    return intent
            
            return Intent.UNKNOWN
            
        except Exception as e:
            print(f"Error detecting intent with OpenAI: {e}")
            return self._keyword_intent_detection(user_message, user_role)
    
    def _keyword_intent_detection(self, user_message: str, user_role: str) -> Intent:
        """Fallback keyword-based intent detection."""
        message_lower = user_message.lower()
        
        # Navigation keywords
        nav_keywords = {
            "attendance": Intent.NAVIGATE_ATTENDANCE,
            "leave": Intent.NAVIGATE_LEAVE,
            "payroll": Intent.NAVIGATE_PAYROLL,
            "salary": Intent.NAVIGATE_PAYROLL,
            "payslip": Intent.NAVIGATE_PAYROLL,
            "skill": Intent.NAVIGATE_CV_SKILLS,
            "cv": Intent.NAVIGATE_CV_SKILLS,
            "announcement": Intent.NAVIGATE_ANNOUNCEMENTS,
            "news": Intent.NAVIGATE_ANNOUNCEMENTS,
            "holiday": Intent.NAVIGATE_HOLIDAYS,
            "employee": Intent.NAVIGATE_EMPLOYEES if user_role == "admin" else Intent.UNKNOWN,
            "report": Intent.NAVIGATE_REPORTS if user_role == "admin" else Intent.UNKNOWN
        }
        
        # Information retrieval keywords
        info_keywords = {
            "my attendance": Intent.VIEW_ATTENDANCE,
            "check in": Intent.VIEW_ATTENDANCE,
            "check out": Intent.VIEW_ATTENDANCE,
            "leave balance": Intent.VIEW_LEAVE_BALANCE,
            "leave history": Intent.VIEW_LEAVE_HISTORY,
            "my salary": Intent.VIEW_SALARY,
            "my payslip": Intent.VIEW_PAYSLIP,
            "my holidays": Intent.VIEW_HOLIDAYS,
            "upcoming holidays": Intent.VIEW_HOLIDAYS,
            "announcements": Intent.VIEW_ANNOUNCEMENTS
        }
        
        # Action keywords
        action_keywords = {
            "apply leave": Intent.APPLY_LEAVE,
            "request leave": Intent.APPLY_LEAVE,
            "update skill": Intent.UPDATE_SKILLS,
            "add skill": Intent.UPDATE_SKILLS,
            "add certification": Intent.UPDATE_CERTIFICATION,
            "update certification": Intent.UPDATE_CERTIFICATION
        }
        
        # Admin keywords
        admin_keywords = {
            "search employee": Intent.SEARCH_EMPLOYEES,
            "find employee": Intent.SEARCH_EMPLOYEES,
            "approve leave": Intent.APPROVE_LEAVE,
            "reject leave": Intent.REJECT_LEAVE,
            "create announcement": Intent.CREATE_ANNOUNCEMENT,
            "add holiday": Intent.MANAGE_HOLIDAY,
            "generate report": Intent.GENERATE_REPORT
        }
        
        # Check admin keywords first
        if user_role == "admin":
            for keyword, intent in admin_keywords.items():
                if keyword in message_lower:
                    return intent
        
        # Check action keywords
        for keyword, intent in action_keywords.items():
            if keyword in message_lower:
                return intent
        
        # Check information keywords
        for keyword, intent in info_keywords.items():
            if keyword in message_lower:
                return intent
        
        # Check navigation keywords
        for keyword, intent in nav_keywords.items():
            if keyword in message_lower:
                return intent
        
        # Check for help
        if any(word in message_lower for word in ["help", "what can you do", "how do i"]):
            return Intent.HELP
        
        return Intent.UNKNOWN
    
    def _generate_response(
        self,
        user_message: str,
        intent: Intent,
        user_role: str,
        available_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate AI response based on intent and available data."""
        if not self.client:
            return self._rule_based_response(intent, user_role, available_data, context)
        
        try:
            prompt = RESPONSE_GENERATION_PROMPT.format(
                user_message=user_message,
                intent=intent.value,
                user_role=user_role,
                available_data=str(available_data) if available_data else "None",
                context=str(context) if context else "None"
            )
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating response with OpenAI: {e}")
            return self._rule_based_response(intent, user_role, available_data, context)
    
    def _rule_based_response(
        self,
        intent: Intent,
        user_role: str,
        available_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Fallback rule-based response generation."""
        
        # Navigation responses
        if intent == Intent.NAVIGATE_ATTENDANCE:
            return "You can manage your attendance from the Attendance section. You can check in, check out, and view your attendance history there."
        elif intent == Intent.NAVIGATE_LEAVE:
            return "You can apply for leave and view your leave balance from the Leave Management section."
        elif intent == Intent.NAVIGATE_PAYROLL:
            return "You can view your salary details, payroll history, and download payslips from the Payroll section."
        elif intent == Intent.NAVIGATE_CV_SKILLS:
            return "You can update your skills, tools, projects, work experience, and certifications from the CV/Skills section."
        elif intent == Intent.NAVIGATE_ANNOUNCEMENTS:
            return "You can view company announcements and updates from the Announcements section."
        elif intent == Intent.NAVIGATE_HOLIDAYS:
            return "You can view the holiday calendar from the Holiday section."
        elif intent == Intent.NAVIGATE_EMPLOYEES and user_role == "admin":
            return "You can manage employees from the Employee Management section. You can add, edit, and view employee profiles."
        elif intent == Intent.NAVIGATE_REPORTS and user_role == "admin":
            return "You can generate attendance, leave, and employee reports from the Reports & Analytics section."
        
        # Information responses
        elif intent == Intent.VIEW_ATTENDANCE and available_data:
            attendance = available_data.get("attendance", [])
            if attendance:
                latest = attendance[0]
                return f"Your latest attendance record:\nDate: {latest['date']}\nCheck-in: {latest['check_in']}\nCheck-out: {latest['check_out']}\nWorking hours: {latest['working_hours']}\nStatus: {latest['status']}"
            return "No attendance records found."
        
        elif intent == Intent.VIEW_LEAVE_BALANCE and available_data:
            balances = available_data.get("leave_balance", [])
            if balances:
                balance_text = "\n".join([f"{b['leave_type']}: {b['remaining_days']} days remaining" for b in balances])
                return f"Your leave balance:\n{balance_text}"
            return "No leave balance information found."
        
        elif intent == Intent.VIEW_HOLIDAYS and available_data:
            holidays = available_data.get("holidays", [])
            if holidays:
                holiday_text = "\n".join([f"{h['name']}: {h['date']} ({h['holiday_type']})" for h in holidays[:5]])
                return f"Upcoming holidays:\n{holiday_text}"
            return "No holidays found."
        
        elif intent == Intent.VIEW_ANNOUNCEMENTS and available_data:
            announcements = available_data.get("announcements", [])
            if announcements:
                announcement_text = "\n".join([f"{a['title']}: {a['content'][:100]}..." for a in announcements[:3]])
                return f"Latest announcements:\n{announcement_text}"
            return "No announcements found."
        
        # Admin responses
        elif intent == Intent.SEARCH_EMPLOYEES and available_data:
            employees = available_data.get("employees", [])
            if employees:
                emp_text = "\n".join([f"{e['name']} ({e['employee_code']}) - {e['department']}" for e in employees[:5]])
                return f"Found employees:\n{emp_text}"
            return "No employees found matching your search."
        
        elif intent == Intent.APPROVE_LEAVE and available_data:
            requests = available_data.get("pending_requests", [])
            if requests:
                req_text = "\n".join([f"{r['employee_name']} - {r['leave_type']} ({r['total_days']} days)" for r in requests[:5]])
                return f"Pending leave requests:\n{req_text}"
            return "No pending leave requests."
        
        # Action responses (require confirmation)
        elif intent == Intent.APPLY_LEAVE:
            return "To apply for leave, please provide the leave type, start date, end date, and reason. I'll need your confirmation before submitting the request."
        
        elif intent == Intent.UPDATE_SKILLS:
            return "To update your skills, please specify the skill name and your proficiency level (1-5). I'll need your confirmation before updating."
        
        # Help response
        elif intent == Intent.HELP:
            return f"I can help you with:\n- Navigating to different HRMS sections\n- Viewing your attendance, leave balance, payroll, and payslips\n- Applying for leave\n- Updating your skills and certifications\n- Viewing holidays and announcements\n\n{INTENT_DESCRIPTIONS.get(intent, '')}"
        
        # Unknown intent
        elif intent == Intent.UNKNOWN:
            return "I'm sorry, I can only assist with PeopleHub HRMS-related questions and portal navigation. Is there something specific about attendance, leave, payroll, or other HRMS features I can help you with?"
        
        return "I understand your request. Let me help you with that."
    
    def process_message(
        self,
        user_message: str,
        user_id: str,
        user_role: str,
        employee_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Process a user message and generate a response."""
        
        # Detect intent
        intent = self._detect_intent(user_message, user_role)
        
        # Check permissions
        if not has_permission(user_role, intent):
            return {
                "response": "I'm sorry, you don't have permission to perform this action. Please contact your administrator if you need access to this feature.",
                "intent": intent.value,
                "action_required": False,
                "session_id": session_id
            }
        
        # Initialize HRMS tools
        tools = HRMSTools(user_id, user_role, employee_id)
        
        # Execute appropriate tool based on intent
        available_data = None
        action_required = False
        action_type = None
        action_data = None
        
        try:
            if intent == Intent.VIEW_ATTENDANCE:
                available_data = tools.get_my_attendance()
            elif intent == Intent.VIEW_LEAVE_BALANCE:
                available_data = tools.get_my_leave_balance()
            elif intent == Intent.VIEW_LEAVE_HISTORY:
                available_data = tools.get_my_leave_history()
            elif intent == Intent.VIEW_PAYROLL:
                available_data = tools.get_my_payroll()
            elif intent == Intent.VIEW_PAYSLIP:
                available_data = tools.get_my_payslips()
            elif intent == Intent.VIEW_HOLIDAYS:
                available_data = tools.get_holidays()
            elif intent == Intent.VIEW_ANNOUNCEMENTS:
                available_data = tools.get_announcements()
            elif intent == Intent.UPDATE_SKILLS:
                available_data = tools.get_my_skills()
                action_required = True
                action_type = "update_skills"
            elif intent == Intent.SEARCH_EMPLOYEES and user_role == "admin":
                # Extract name from message
                name_match = re.search(r'(?:search|find)\s+(?:for\s+)?(.+)', user_message.lower())
                name = name_match.group(1) if name_match else ""
                available_data = tools.search_employees(name)
            elif intent == Intent.APPROVE_LEAVE and user_role == "admin":
                available_data = tools.get_pending_leave_requests()
            elif intent == Intent.GENERATE_REPORT and user_role == "admin":
                available_data = tools.get_attendance_overview()
        
        except Exception as e:
            print(f"Error executing tool: {e}")
            available_data = {"error": str(e)}
        
        # Generate response
        response = self._generate_response(
            user_message=user_message,
            intent=intent,
            user_role=user_role,
            available_data=available_data,
            context={"session_id": session_id}
        )
        
        # Determine if navigation action is needed
        if intent.name.startswith("NAVIGATE_"):
            action_required = True
            action_type = "navigate"
            action_data = {"page": intent.name.replace("NAVIGATE_", "").lower()}
        
        return {
            "response": response,
            "intent": intent.value,
            "action_required": action_required,
            "action_type": action_type,
            "action_data": action_data,
            "session_id": session_id
        }