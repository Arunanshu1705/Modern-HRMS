from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.base import BaseModel, TimestampMixin
class ChatSession(BaseModel, TimestampMixin):
    """Chat session model for AI chatbot conversations."""
    __tablename__ = "chat_sessions"
    user_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    # Relationships
    messages = relationship("ChatMessage", back_populates="session")
    user = relationship("Employee", back_populates="chat_sessions")
class ChatMessage(BaseModel, TimestampMixin):
    """Chat message model for individual chatbot messages."""
    __tablename__ = "chat_messages"
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    message = Column(Text, nullable=False)
    sender = Column(String(20), nullable=False)  # 'user' or 'bot'
    intent = Column(String(50))
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    user = relationship("Employee", back_populates="chat_messages", foreign_keys="ChatMessage.user_id")