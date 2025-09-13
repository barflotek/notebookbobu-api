"""
Client domain entity following Document patterns
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from datetime import datetime


class ClientType(str, Enum):
    """Client skill level and type"""
    PROSPECT = "prospect"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    INSTRUCTOR = "instructor"


class ClientStatus(str, Enum):
    """Client relationship status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"
    ARCHIVED = "archived"


class ContactMethod(str, Enum):
    """Preferred contact method"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    IN_PERSON = "in_person"


class Equipment(str, Enum):
    """Fencing equipment preferences"""
    SABRE = "sabre"
    EPEE = "epee"
    FOIL = "foil"
    ALL = "all"
    NONE = "none"


class Client(BaseModel):
    """
    Client entity - core business relationship
    Follows Document entity patterns for consistency
    """
    
    # Core identification
    id: Optional[str] = None
    user_id: str  # Business owner/coach who manages this client
    
    # Basic info (Must-Have from CRM spec)
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    # Business context
    client_type: ClientType = ClientType.PROSPECT
    status: ClientStatus = ClientStatus.PROSPECT
    
    # Preferences
    preferred_contact: ContactMethod = ContactMethod.EMAIL
    equipment_preference: Equipment = Equipment.NONE
    
    # Emergency contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    # Business tracking
    referral_source: Optional[str] = None  # Who referred them
    referred_clients: List[str] = []  # IDs of clients they referred
    
    # Lesson context
    total_lessons: int = 0
    last_lesson_date: Optional[datetime] = None
    
    # Payment context
    outstanding_balance: float = 0.0
    payment_preference: Optional[str] = None  # "monthly", "per_lesson", "package"
    
    # Analytics (following Document pattern)
    engagement_score: float = 0.0  # Based on communication frequency
    document_count: int = 0  # How many documents are associated with this client
    
    # Timestamps
    join_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    
    # Flexible metadata for business-specific fields
    metadata: Dict[str, Any] = {}
    
    class Config:
        """Pydantic configuration following Document patterns"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class ClientInsights(BaseModel):
    """
    AI-generated insights about client
    Similar to Document processing results
    """
    
    client_id: str
    
    # Communication analysis
    communication_frequency: str  # "high", "medium", "low"
    last_interaction_days: int
    preferred_topics: List[str] = []
    
    # Business insights
    risk_level: str = "low"  # "high", "medium", "low" 
    engagement_trend: str = "stable"  # "improving", "declining", "stable"
    
    # AI suggestions
    suggested_actions: List[str] = []
    follow_up_priority: str = "normal"  # "urgent", "high", "normal", "low"
    
    # Generated content
    summary: Optional[str] = None
    key_notes: List[str] = []
    
    # Timestamps
    generated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }