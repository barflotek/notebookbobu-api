"""
Communication repository interface for unified client interaction history
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.client.entity import Communication


class CommunicationRepositoryInterface(ABC):
    """Communication repository interface for client interaction tracking"""
    
    @abstractmethod
    async def create_communication(self, communication: Communication) -> Communication:
        """Record a new client communication"""
        pass
    
    @abstractmethod
    async def get_communications_by_client(
        self, 
        client_id: str, 
        user_id: str,
        limit: int = 50, 
        offset: int = 0
    ) -> List[Communication]:
        """Get communication timeline for a client"""
        pass
    
    @abstractmethod
    async def get_communication_by_id(self, communication_id: str, user_id: str) -> Optional[Communication]:
        """Get specific communication record"""
        pass
    
    @abstractmethod
    async def update_communication(self, communication: Communication) -> Communication:
        """Update communication record"""
        pass
    
    @abstractmethod
    async def delete_communication(self, communication_id: str, user_id: str) -> bool:
        """Delete communication record"""
        pass
    
    @abstractmethod
    async def get_communications_requiring_followup(self, user_id: str) -> List[Communication]:
        """Get communications that need follow-up"""
        pass
    
    @abstractmethod
    async def link_document_to_client(
        self, 
        document_id: str, 
        client_id: str, 
        user_id: str,
        subject: Optional[str] = None
    ) -> Communication:
        """Create communication record linking document to client"""
        pass
    
    @abstractmethod
    async def get_recent_client_activity(
        self, 
        user_id: str, 
        days: int = 7, 
        limit: int = 20
    ) -> List[Communication]:
        """Get recent client communications across all clients"""
        pass