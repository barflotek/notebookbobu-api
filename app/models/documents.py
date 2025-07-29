"""
Document data models
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class DocumentResponse(BaseModel):
    """Document response model"""
    id: str
    title: str
    summary: Optional[str] = None
    bullet_points: Optional[str] = None
    q_and_a: Optional[str] = None
    mindmap_html: Optional[str] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: datetime


class DocumentProcessResponse(BaseModel):
    """Document processing response"""
    success: bool
    document_id: Optional[str] = None
    summary: Optional[str] = None
    bullet_points: Optional[str] = None
    q_and_a: Optional[str] = None
    mindmap_html: Optional[str] = None
    error: Optional[str] = None


class DocumentCreateRequest(BaseModel):
    """Document creation request"""
    title: str
    content: str
    file_type: str = "txt"