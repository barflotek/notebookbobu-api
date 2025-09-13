"""
Client service implementation following Document service patterns
"""

import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.domain.client.entity import (
    Client, ClientInsights, Communication, Task, 
    ClientType, ClientStatus, CommunicationType, TaskStatus, TaskPriority
)
from app.domain.client.repository import (
    ClientRepositoryInterface, 
    CommunicationRepositoryInterface,
    TaskRepositoryInterface
)


class ClientServiceInterface:
    """Client service interface"""
    
    async def create_client_from_document(
        self, 
        document_id: str,
        user_id: str,
        client_info: Dict[str, Any]
    ) -> Client:
        """Create client from document processing (main use case)"""
        pass
    
    async def link_document_to_client(
        self,
        document_id: str, 
        client_id: str, 
        user_id: str,
        subject: Optional[str] = None
    ) -> Communication:
        """Link processed document to existing client"""
        pass
    
    async def get_client_insights(self, client_id: str, user_id: str) -> Optional[ClientInsights]:
        """Get AI-generated insights for client"""
        pass
    
    async def suggest_client_actions(self, client_id: str, user_id: str) -> List[Task]:
        """AI-suggested follow-up actions"""
        pass


class ClientService(ClientServiceInterface):
    """Client service implementation with AI-powered insights"""
    
    def __init__(
        self,
        client_repo: ClientRepositoryInterface,
        communication_repo: CommunicationRepositoryInterface,
        task_repo: TaskRepositoryInterface
    ):
        self.client_repo = client_repo
        self.communication_repo = communication_repo
        self.task_repo = task_repo
    
    async def create_client_from_document(
        self, 
        document_id: str,
        user_id: str,
        client_info: Dict[str, Any]
    ) -> Client:
        """
        Create client from document analysis (primary workflow)
        This is called when AI detects client info in processed documents
        """
        
        # Create client entity
        client = Client(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=client_info.get("name", "Unknown Client"),
            email=client_info.get("email"),
            phone=client_info.get("phone"),
            client_type=ClientType(client_info.get("type", "prospect")),
            status=ClientStatus.PROSPECT,
            created_at=datetime.utcnow(),
            join_date=datetime.utcnow(),
            metadata=client_info.get("metadata", {})
        )
        
        # Save client
        client = await self.client_repo.create_client(client)
        
        # Create communication record linking document
        await self.communication_repo.link_document_to_client(
            document_id=document_id,
            client_id=client.id,
            user_id=user_id,
            subject=f"Document analysis - {client_info.get('name', 'New client')}"
        )
        
        return client
    
    async def link_document_to_client(
        self,
        document_id: str, 
        client_id: str, 
        user_id: str,
        subject: Optional[str] = None
    ) -> Communication:
        """Link processed document to existing client"""
        
        communication = await self.communication_repo.link_document_to_client(
            document_id=document_id,
            client_id=client_id,
            user_id=user_id,
            subject=subject
        )
        
        # Update client engagement metrics
        await self.client_repo.update_client_engagement(
            client_id=client_id,
            document_count=1,  # Increment
            last_contact=datetime.utcnow().isoformat()
        )
        
        return communication
    
    async def get_client_with_context(self, client_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get client with full context (communications, tasks, insights)"""
        
        client = await self.client_repo.get_client_by_id(client_id, user_id)
        if not client:
            return None
        
        # Get recent communications (timeline view)
        communications = await self.communication_repo.get_communications_by_client(
            client_id=client_id,
            user_id=user_id,
            limit=20
        )
        
        # Get active tasks
        tasks = await self.task_repo.get_tasks_by_client(
            client_id=client_id,
            user_id=user_id,
            status=TaskStatus.PENDING
        )
        
        # Get AI insights
        insights = await self.get_client_insights(client_id, user_id)
        
        return {
            "client": client,
            "communications": communications,
            "active_tasks": tasks,
            "insights": insights,
            "stats": {
                "total_communications": len(communications),
                "pending_tasks": len(tasks),
                "days_since_contact": self._calculate_days_since_contact(communications)
            }
        }
    
    async def get_client_insights(self, client_id: str, user_id: str) -> Optional[ClientInsights]:
        """Generate AI insights for client based on communications and documents"""
        
        # Get client and communications for analysis
        client = await self.client_repo.get_client_by_id(client_id, user_id)
        if not client:
            return None
        
        communications = await self.communication_repo.get_communications_by_client(
            client_id, user_id, limit=50
        )
        
        # Mock AI analysis (replace with real AI service)
        insights = self._generate_mock_insights(client, communications)
        
        return insights
    
    async def suggest_client_actions(self, client_id: str, user_id: str) -> List[Task]:
        """Generate AI-suggested follow-up actions"""
        
        insights = await self.get_client_insights(client_id, user_id)
        if not insights:
            return []
        
        suggested_tasks = []
        
        # Rule-based suggestions (replace with AI)
        if insights.last_interaction_days > 30:
            task = Task(
                id=str(uuid.uuid4()),
                client_id=client_id,
                user_id=user_id,
                title="Follow up - No contact in 30+ days",
                description=f"Client hasn't been contacted in {insights.last_interaction_days} days",
                type="follow_up",
                priority=TaskPriority.HIGH,
                is_ai_suggested=True,
                ai_reasoning="Long gap in communication detected",
                due_date=datetime.utcnow() + timedelta(days=1),
                created_at=datetime.utcnow()
            )
            suggested_tasks.append(task)
        
        if insights.risk_level == "high":
            task = Task(
                id=str(uuid.uuid4()),
                client_id=client_id,
                user_id=user_id,
                title="Risk Assessment - High risk client",
                description="Client showing signs of disengagement",
                type="follow_up", 
                priority=TaskPriority.URGENT,
                is_ai_suggested=True,
                ai_reasoning="AI detected high risk of client churn",
                due_date=datetime.utcnow(),
                created_at=datetime.utcnow()
            )
            suggested_tasks.append(task)
        
        return suggested_tasks
    
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get CRM dashboard data for user"""
        
        # Today's tasks
        today_tasks = await self.task_repo.get_today_tasks(user_id)
        overdue_tasks = await self.task_repo.get_overdue_tasks(user_id)
        
        # Recent client activity
        recent_activity = await self.communication_repo.get_recent_client_activity(
            user_id=user_id,
            days=7,
            limit=10
        )
        
        # Clients needing follow-up
        stale_clients = await self.client_repo.get_clients_needing_followup(
            user_id=user_id,
            days_since_contact=21
        )
        
        # Active clients
        active_clients = await self.client_repo.get_clients_by_status(
            user_id=user_id,
            status="active",
            limit=100
        )
        
        return {
            "today_tasks": today_tasks,
            "overdue_tasks": overdue_tasks,
            "recent_activity": recent_activity,
            "stale_clients": stale_clients,
            "stats": {
                "active_clients": len(active_clients),
                "tasks_due_today": len(today_tasks),
                "overdue_tasks": len(overdue_tasks),
                "clients_needing_followup": len(stale_clients)
            }
        }
    
    def _generate_mock_insights(self, client: Client, communications: List[Communication]) -> ClientInsights:
        """Generate mock AI insights (replace with real AI service)"""
        
        days_since_contact = self._calculate_days_since_contact(communications)
        
        # Mock analysis
        insights = ClientInsights(
            client_id=client.id,
            communication_frequency="medium" if len(communications) > 5 else "low",
            last_interaction_days=days_since_contact,
            preferred_topics=["lessons", "equipment"],  # Would be extracted from content
            risk_level="high" if days_since_contact > 45 else "low",
            engagement_trend="declining" if days_since_contact > 30 else "stable",
            suggested_actions=[
                "Schedule follow-up call",
                "Send lesson reminder" if client.client_type != ClientType.PROSPECT else "Send welcome information"
            ],
            follow_up_priority="high" if days_since_contact > 30 else "normal",
            summary=f"Client with {len(communications)} interactions. Last contact {days_since_contact} days ago.",
            key_notes=[
                f"Client type: {client.client_type.value}",
                f"Preferred equipment: {client.equipment_preference.value}",
                f"Total lessons: {client.total_lessons}"
            ],
            generated_at=datetime.utcnow()
        )
        
        return insights
    
    def _calculate_days_since_contact(self, communications: List[Communication]) -> int:
        """Calculate days since last client contact"""
        if not communications:
            return 9999
        
        latest_communication = max(communications, key=lambda c: c.occurred_at)
        return (datetime.utcnow() - latest_communication.occurred_at).days