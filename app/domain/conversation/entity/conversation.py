"""
Conversation domain entity following Coze Studio patterns
"""

from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Conversation status"""
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class MessageType(str, Enum):
    """Message type"""
    TEXT = "text"
    DOCUMENT_QUERY = "document_query"
    SUMMARY = "summary"
    PODCAST_GENERATION = "podcast_generation"


class Message(BaseModel):
    """Message entity"""
    
    id: Optional[str] = None
    conversation_id: str
    role: MessageRole
    content: str
    message_type: MessageType = MessageType.TEXT
    
    # Context and references
    document_ids: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class Conversation(BaseModel):
    """Conversation entity with comprehensive metadata"""
    
    # Core identification
    id: Optional[str] = None
    user_id: str
    title: str
    
    # Conversation metadata
    status: ConversationStatus = ConversationStatus.ACTIVE
    message_count: int = 0
    
    # Document context
    document_ids: List[str] = []
    
    # Analytics
    total_tokens: Optional[int] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = {}

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ChatSession(BaseModel):
    """Chat session for managing conversation state"""
    
    conversation_id: str
    user_id: str
    context_documents: List[str] = []
    session_metadata: Dict[str, Any] = {}
    
    # Session state
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }