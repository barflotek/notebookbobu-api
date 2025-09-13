"""
Communication entity - unified timeline for client interactions
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class CommunicationType(str, Enum):
    """Types of client communications"""
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_PERSON = "in_person"
    DOCUMENT = "document"  # Links to processed documents
    NOTE = "note"  # Manual notes


class Communication(BaseModel):
    """
    Communication record linking clients to all interactions
    This bridges documents and direct communications
    """
    
    # Core identification
    id: Optional[str] = None
    client_id: str
    user_id: str  # Staff member who handled this communication
    
    # Communication details
    type: CommunicationType
    subject: Optional[str] = None
    content: Optional[str] = None
    
    # Document linkage (when communication_type == DOCUMENT)
    document_id: Optional[str] = None
    
    # Call/meeting specific
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None  # "follow_up_needed", "closed", "scheduled_lesson"
    
    # Email/message specific  
    direction: str = "outbound"  # "inbound", "outbound"
    is_read: bool = True
    
    # Follow-up tracking
    requires_followup: bool = False
    followup_date: Optional[datetime] = None
    followup_completed: bool = False
    
    # AI analysis (similar to document processing)
    sentiment: Optional[str] = None  # "positive", "neutral", "negative"
    key_topics: list = []
    urgency_level: str = "normal"  # "urgent", "high", "normal", "low"
    
    # Timestamps
    occurred_at: datetime
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Flexible metadata
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }