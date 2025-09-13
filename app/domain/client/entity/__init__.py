"""
Client domain entity exports
"""

from .client import Client, ClientType, ClientStatus, ContactMethod, Equipment
from .communication import Communication, CommunicationType
from .task import Task, TaskStatus, TaskPriority

__all__ = [
    "Client", "ClientType", "ClientStatus", "ContactMethod", "Equipment",
    "Communication", "CommunicationType", 
    "Task", "TaskStatus", "TaskPriority"
]