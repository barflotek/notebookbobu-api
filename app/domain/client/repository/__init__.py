"""
Client domain repository interfaces
"""

from .client_repository import ClientRepositoryInterface
from .communication_repository import CommunicationRepositoryInterface  
from .task_repository import TaskRepositoryInterface

__all__ = [
    "ClientRepositoryInterface",
    "CommunicationRepositoryInterface", 
    "TaskRepositoryInterface"
]