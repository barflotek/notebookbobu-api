"""
Task entity for client follow-ups and action items
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class TaskStatus(str, Enum):
    """Task completion status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority levels"""
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class Task(BaseModel):
    """
    Task entity for client relationship management
    Supports both manual tasks and AI-suggested actions
    """
    
    # Core identification
    id: Optional[str] = None
    client_id: str
    user_id: str  # Assigned to (staff member)
    
    # Task details
    title: str
    description: Optional[str] = None
    type: str = "follow_up"  # "follow_up", "payment_reminder", "lesson_scheduling", "general"
    
    # Scheduling
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Status and priority
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.NORMAL
    
    # AI context
    is_ai_suggested: bool = False
    ai_reasoning: Optional[str] = None  # Why AI suggested this task
    
    # Communication linkage
    related_communication_id: Optional[str] = None
    related_document_id: Optional[str] = None
    
    # Results tracking
    outcome: Optional[str] = None
    notes: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Flexible metadata
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }