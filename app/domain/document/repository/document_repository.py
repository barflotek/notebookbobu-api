"""
Document repository interface following Coze Studio patterns
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.domain.document.entity import Document, DocumentChunk


class DocumentRepositoryInterface(ABC):
    """Document repository interface for data access abstraction"""
    
    @abstractmethod
    async def create_document(self, document: Document) -> Document:
        """Create a new document"""
        pass
    
    @abstractmethod
    async def get_document_by_id(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get document by ID with user ownership check"""
        pass
    
    @abstractmethod
    async def get_documents_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Document]:
        """Get documents for a user with pagination"""
        pass
    
    @abstractmethod
    async def update_document(self, document: Document) -> Document:
        """Update document"""
        pass
    
    @abstractmethod
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document with user ownership check"""
        pass
    
    @abstractmethod
    async def update_document_status(self, document_id: str, status: str, status_message: Optional[str] = None) -> bool:
        """Update document processing status"""
        pass
    
    @abstractmethod
    async def get_documents_by_status(self, status: str, limit: int = 100) -> List[Document]:
        """Get documents by processing status"""
        pass


class DocumentChunkRepositoryInterface(ABC):
    """Document chunk repository interface"""
    
    @abstractmethod
    async def create_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Create document chunks"""
        pass
    
    @abstractmethod
    async def get_chunks_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        pass
    
    @abstractmethod
    async def delete_chunks_by_document_id(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        pass
    
    @abstractmethod
    async def search_chunks(self, query: str, user_id: str, limit: int = 10) -> List[DocumentChunk]:
        """Search chunks by content (for RAG implementation)"""
        pass