"""
Task repository interface for client follow-up and action management
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from app.domain.client.entity import Task, TaskStatus, TaskPriority


class TaskRepositoryInterface(ABC):
    """Task repository interface for client action items"""
    
    @abstractmethod
    async def create_task(self, task: Task) -> Task:
        """Create a new client task"""
        pass
    
    @abstractmethod
    async def get_task_by_id(self, task_id: str, user_id: str) -> Optional[Task]:
        """Get specific task by ID"""
        pass
    
    @abstractmethod
    async def get_tasks_by_client(
        self, 
        client_id: str, 
        user_id: str,
        status: Optional[TaskStatus] = None,
        limit: int = 50
    ) -> List[Task]:
        """Get tasks for a specific client"""
        pass
    
    @abstractmethod
    async def get_tasks_by_user(
        self,
        user_id: str,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        limit: int = 100
    ) -> List[Task]:
        """Get tasks assigned to a user"""
        pass
    
    @abstractmethod
    async def update_task(self, task: Task) -> Task:
        """Update task status, notes, or completion"""
        pass
    
    @abstractmethod
    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task"""
        pass
    
    @abstractmethod
    async def get_overdue_tasks(self, user_id: str) -> List[Task]:
        """Get tasks past their due date"""
        pass
    
    @abstractmethod
    async def get_today_tasks(self, user_id: str) -> List[Task]:
        """Get tasks due today"""
        pass
    
    @abstractmethod
    async def get_upcoming_tasks(self, user_id: str, days_ahead: int = 7) -> List[Task]:
        """Get tasks due in the next N days"""
        pass
    
    @abstractmethod
    async def complete_task(self, task_id: str, user_id: str, outcome: Optional[str] = None) -> bool:
        """Mark task as completed with optional outcome"""
        pass