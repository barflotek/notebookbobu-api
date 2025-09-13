"""
Client-related Pydantic models for API responses
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ClientResponse(BaseModel):
    """Client response model for API"""
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    
    client_type: str
    status: str
    preferred_contact: str
    equipment_preference: str
    
    total_lessons: int = 0
    outstanding_balance: float = 0.0
    document_count: int = 0
    engagement_score: float = 0.0
    
    created_at: Optional[str] = None
    last_contact_date: Optional[str] = None


class ClientCreateRequest(BaseModel):
    """Client creation request"""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    client_type: str = "prospect"
    equipment_preference: str = "none"


class ClientUpdateRequest(BaseModel):
    """Client update request"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    client_type: Optional[str] = None
    status: Optional[str] = None
    equipment_preference: Optional[str] = None


class CommunicationResponse(BaseModel):
    """Communication timeline response"""
    id: str
    client_id: str
    type: str
    subject: Optional[str] = None
    content: Optional[str] = None
    document_id: Optional[str] = None
    duration_minutes: Optional[int] = None
    outcome: Optional[str] = None
    occurred_at: str
    requires_followup: bool = False


class TaskResponse(BaseModel):
    """Task response model"""
    id: str
    client_id: str
    title: str
    description: Optional[str] = None
    type: str
    status: str
    priority: str
    due_date: Optional[str] = None
    is_ai_suggested: bool = False
    ai_reasoning: Optional[str] = None
    created_at: str


class TaskCreateRequest(BaseModel):
    """Task creation request"""
    client_id: str
    title: str
    description: Optional[str] = None
    type: str = "follow_up"
    priority: str = "normal"
    due_date: Optional[datetime] = None


class ClientInsightsResponse(BaseModel):
    """Client insights API response"""
    client_id: str
    communication_frequency: str
    last_interaction_days: int
    risk_level: str
    engagement_trend: str
    suggested_actions: List[str]
    summary: Optional[str] = None
    key_notes: List[str] = []


class ClientDashboardResponse(BaseModel):
    """CRM dashboard response"""
    stats: Dict[str, Any]
    today_tasks: List[TaskResponse]
    overdue_tasks: List[TaskResponse]
    recent_activity: List[CommunicationResponse]
    stale_clients: List[ClientResponse]


class DocumentClientLinkRequest(BaseModel):
    """Request to link document to client"""
    client_id: str
    subject: Optional[str] = None


class ClientContextResponse(BaseModel):
    """Full client context response"""
    client: ClientResponse
    communications: List[CommunicationResponse]
    active_tasks: List[TaskResponse]
    insights: Optional[ClientInsightsResponse] = None
    stats: Dict[str, Any]