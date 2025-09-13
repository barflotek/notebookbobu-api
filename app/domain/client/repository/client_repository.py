"""
Client repository interface following Document repository patterns
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.client.entity import Client, ClientInsights


class ClientRepositoryInterface(ABC):
    """Client repository interface for data access abstraction"""
    
    @abstractmethod
    async def create_client(self, client: Client) -> Client:
        """Create a new client"""
        pass
    
    @abstractmethod
    async def get_client_by_id(self, client_id: str, user_id: str) -> Optional[Client]:
        """Get client by ID with user ownership check"""
        pass
    
    @abstractmethod
    async def get_clients_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Client]:
        """Get clients for a user with pagination"""
        pass
    
    @abstractmethod
    async def update_client(self, client: Client) -> Client:
        """Update client information"""
        pass
    
    @abstractmethod
    async def delete_client(self, client_id: str, user_id: str) -> bool:
        """Delete client with user ownership check"""
        pass
    
    @abstractmethod
    async def search_clients(self, user_id: str, query: str, limit: int = 20) -> List[Client]:
        """Search clients by name, email, or phone"""
        pass
    
    @abstractmethod
    async def get_clients_by_status(self, user_id: str, status: str, limit: int = 100) -> List[Client]:
        """Get clients by status (active, inactive, prospect)"""
        pass
    
    @abstractmethod
    async def get_clients_needing_followup(self, user_id: str, days_since_contact: int = 30) -> List[Client]:
        """Get clients who haven't been contacted recently"""
        pass
    
    @abstractmethod
    async def update_client_engagement(self, client_id: str, document_count: int, last_contact: Optional[str] = None) -> bool:
        """Update client engagement metrics"""
        pass


class ClientInsightsRepositoryInterface(ABC):
    """Repository for AI-generated client insights"""
    
    @abstractmethod
    async def create_insights(self, insights: ClientInsights) -> ClientInsights:
        """Create or update client insights"""
        pass
    
    @abstractmethod
    async def get_insights_by_client(self, client_id: str) -> Optional[ClientInsights]:
        """Get latest insights for a client"""
        pass
    
    @abstractmethod
    async def get_clients_by_risk_level(self, user_id: str, risk_level: str) -> List[str]:
        """Get client IDs by AI-assessed risk level"""
        pass