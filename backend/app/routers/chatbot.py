from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import uuid
from app.database.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.chatbot import ChatRequest, ChatResponse, ChatHistoryResponse
from app.ai.service import AIChatbotService
from app.models import ChatSession, ChatMessage, Employee, User

router = APIRouter()
chatbot_service = AIChatbotService()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Process chat message with AI chatbot."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    employee_id = employee.id if employee else None
    
    # Handle session
    session_id = chat_request.session_id
    if not session_id:
        # Create new session
        session_id = str(uuid.uuid4())
        new_session = ChatSession(
            user_id=employee_id if employee_id else user.id,
            session_id=session_id,
            is_active=True
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
    else:
        # Get existing session
        session = db.query(ChatSession).filter(
            ChatSession.session_id == session_id
        ).first()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
    
    # Process message with AI service
    try:
        response_data = chatbot_service.process_message(
            user_message=chat_request.message,
            user_id=current_user["user_id"],
            user_role=current_user["role"],
            employee_id=employee_id,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )
    
    # Store user message
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    user_message = ChatMessage(
        session_id=session.id,
        user_id=employee_id if employee_id else user.id,
        message=chat_request.message,
        sender="user",
        intent=response_data.get("intent")
    )
    db.add(user_message)
    
    # Store bot response
    bot_message = ChatMessage(
        session_id=session.id,
        user_id=employee_id if employee_id else user.id,
        message=response_data["response"],
        sender="bot",
        intent=response_data.get("intent")
    )
    db.add(bot_message)
    
    db.commit()
    
    return ChatResponse(
        response=response_data["response"],
        intent=response_data.get("intent"),
        action_required=response_data.get("action_required", False),
        action_type=response_data.get("action_type"),
        action_data=response_data.get("action_data"),
        session_id=session_id
    )


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get chat history for a session."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    employee_id = employee.id if employee else None
    
    # Get session
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Verify user owns this session
    if session.user_id != (employee_id if employee_id else user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this session"
        )
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.asc()).all()
    
    return ChatHistoryResponse(
        session_id=session_id,
        messages=messages
    )


@router.post("/sessions")
async def create_chat_session(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new chat session."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    employee_id = employee.id if employee else None
    
    # Create new session
    session_id = str(uuid.uuid4())
    new_session = ChatSession(
        user_id=employee_id if employee_id else user.id,
        session_id=session_id,
        is_active=True
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return {"session_id": session_id}


@router.get("/sessions")
async def get_chat_sessions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get all chat sessions for current user."""
    # Get user from user_id
    user = db.query(User).filter(User.user_id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get employee from user
    employee = db.query(Employee).filter(Employee.user_id == user.id).first()
    employee_id = employee.id if employee else None
    
    # Get sessions
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == (employee_id if employee_id else user.id),
        ChatSession.is_active == True
    ).order_by(ChatSession.created_at.desc()).limit(20).all()
    
    return {
        "sessions": [
            {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "message_count": len(session.messages)
            }
            for session in sessions
        ]
    }