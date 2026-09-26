from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatMessageBase(BaseModel):
    """Base chat message schema."""
    message: str = Field(..., min_length=1)
    sender: str = Field(..., description="Either 'user' or 'bot'")
    intent: Optional[str] = None


class ChatMessageCreate(ChatMessageBase):
    """Schema for creating chat message."""
    session_id: int
    user_id: int


class ChatMessageResponse(ChatMessageBase):
    """Schema for chat message response."""
    id: int
    session_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatSessionBase(BaseModel):
    """Base chat session schema."""
    session_id: str = Field(..., min_length=1, max_length=100)
    is_active: bool = True


class ChatSessionCreate(ChatSessionBase):
    """Schema for creating chat session."""
    user_id: int


class ChatSessionResponse(ChatSessionBase):
    """Schema for chat session response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat response."""
    response: str
    intent: Optional[str] = None
    action_required: bool = False
    action_type: Optional[str] = None
    action_data: Optional[dict] = None
    session_id: str


class ChatHistoryResponse(BaseModel):
    """Schema for chat history response."""
    session_id: str
    messages: List[ChatMessageResponse]