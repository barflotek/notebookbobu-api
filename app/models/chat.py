"""
Chat and query data models
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class QueryRequest(BaseModel):
    """Query request model"""
    question: str
    document_ids: Optional[List[str]] = None


class QueryResponse(BaseModel):
    """Query response model"""
    success: bool
    answer: Optional[str] = None
    sources: Optional[List[str]] = None
    document_count: Optional[int] = None
    error: Optional[str] = None


class ChatHistoryResponse(BaseModel):
    """Chat history response model"""
    id: str
    question: str
    answer: str
    sources: List[str]
    document_ids: List[str]
    created_at: datetime


class PodcastRequest(BaseModel):
    """Podcast generation request"""
    document_ids: List[str]
    title: Optional[str] = None
    voice_settings: Optional[dict] = None


class PodcastResponse(BaseModel):
    """Podcast generation response"""
    success: bool
    podcast_id: Optional[str] = None
    title: Optional[str] = None
    transcript: Optional[str] = None
    audio_url: Optional[str] = None
    status: str = "generating"
    error: Optional[str] = None