"""
Dependency injection container following Coze Studio patterns
"""

from typing import Optional

from app.services.database import DatabaseService
from app.services.document_processor import DocumentProcessor
from app.domain.document.service.document_service import DocumentService
from app.infrastructure.repository.supabase_document_repository import (
    SupabaseDocumentRepository,
    SupabaseDocumentChunkRepository
)


class Container:
    """Dependency injection container for managing service instances"""
    
    def __init__(self):
        self._database_service: Optional[DatabaseService] = None
        self._document_processor: Optional[DocumentProcessor] = None
        self._document_repository: Optional[SupabaseDocumentRepository] = None
        self._chunk_repository: Optional[SupabaseDocumentChunkRepository] = None
        self._document_service: Optional[DocumentService] = None
    
    @property
    def database_service(self) -> DatabaseService:
        """Get database service singleton"""
        if self._database_service is None:
            self._database_service = DatabaseService()
        return self._database_service
    
    @property
    def document_processor(self) -> DocumentProcessor:
        """Get document processor singleton"""
        if self._document_processor is None:
            self._document_processor = DocumentProcessor()
        return self._document_processor
    
    @property
    def document_repository(self) -> SupabaseDocumentRepository:
        """Get document repository singleton"""
        if self._document_repository is None:
            self._document_repository = SupabaseDocumentRepository(self.database_service)
        return self._document_repository
    
    @property
    def chunk_repository(self) -> SupabaseDocumentChunkRepository:
        """Get chunk repository singleton"""
        if self._chunk_repository is None:
            self._chunk_repository = SupabaseDocumentChunkRepository(self.database_service)
        return self._chunk_repository
    
    @property
    def document_service(self) -> DocumentService:
        """Get document service singleton"""
        if self._document_service is None:
            self._document_service = DocumentService(
                document_repo=self.document_repository,
                chunk_repo=self.chunk_repository,
                processor=self.document_processor
            )
        return self._document_service


# Global container instance
container = Container()