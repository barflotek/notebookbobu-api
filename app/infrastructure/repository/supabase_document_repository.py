"""
Supabase implementation of document repository
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.document.entity import Document, DocumentChunk
from app.domain.document.repository import DocumentRepositoryInterface, DocumentChunkRepositoryInterface
from app.services.database import DatabaseService


class SupabaseDocumentRepository(DocumentRepositoryInterface):
    """Supabase implementation of document repository"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def create_document(self, document: Document) -> Document:
        """Create a new document in Supabase"""
        
        data = {
            "id": document.id,
            "user_id": document.user_id,
            "title": document.title,
            "type": document.type.value,
            "file_extension": document.file_extension,
            "size": document.size,
            "char_count": document.char_count,
            "raw_content": document.raw_content,
            "processed_content": document.processed_content,
            "storage_uri": document.storage_uri,
            "storage_url": document.storage_url,
            "status": document.status.value,
            "status_message": document.status_message,
            "processing_strategy": document.processing_strategy.dict(),
            "hits": document.hits,
            "source": document.source.value,
            "chunk_count": document.chunk_count,
            "chunks": document.chunks,
            "metadata": document.metadata,
            "created_at": document.created_at.isoformat() if document.created_at else datetime.utcnow().isoformat()
        }
        
        result = await self.db.create_document(data)
        return self._map_to_document(result)
    
    async def get_document_by_id(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get document by ID with optional user ownership check"""
        
        filters = {"id": document_id}
        if user_id:
            filters["user_id"] = user_id
            
        result = await self.db.get_document_by_filters(filters)
        return self._map_to_document(result) if result else None
    
    async def get_documents_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Document]:
        """Get documents for a user with pagination"""
        
        results = await self.db.get_documents_by_user(user_id, limit, offset)
        return [self._map_to_document(result) for result in results]
    
    async def update_document(self, document: Document) -> Document:
        """Update document"""
        
        data = {
            "title": document.title,
            "processed_content": document.processed_content,
            "status": document.status.value,
            "status_message": document.status_message,
            "hits": document.hits,
            "chunk_count": document.chunk_count,
            "chunks": document.chunks,
            "metadata": document.metadata,
            "updated_at": datetime.utcnow().isoformat(),
            "processed_at": document.processed_at.isoformat() if document.processed_at else None
        }
        
        result = await self.db.update_document(document.id, data)
        return self._map_to_document(result)
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document with user ownership check"""
        
        return await self.db.delete_document(document_id, user_id)
    
    async def update_document_status(self, document_id: str, status: str, status_message: Optional[str] = None) -> bool:
        """Update document processing status"""
        
        data = {
            "status": status,
            "status_message": status_message,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await self.db.update_document(document_id, data)
        return result is not None
    
    async def get_documents_by_status(self, status: str, limit: int = 100) -> List[Document]:
        """Get documents by processing status"""
        
        results = await self.db.get_documents_by_filters({"status": status}, limit=limit)
        return [self._map_to_document(result) for result in results]
    
    def _map_to_document(self, data: Dict[str, Any]) -> Document:
        """Map database row to Document entity"""
        
        if not data:
            return None
            
        # Parse JSON fields
        processing_strategy = data.get("processing_strategy", {})
        if isinstance(processing_strategy, str):
            processing_strategy = json.loads(processing_strategy)
        
        metadata = data.get("metadata", {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        return Document(
            id=data.get("id"),
            user_id=data.get("user_id"),
            title=data.get("title"),
            type=data.get("type"),
            file_extension=data.get("file_extension"),
            size=data.get("size"),
            char_count=data.get("char_count"),
            raw_content=data.get("raw_content"),
            processed_content=data.get("processed_content"),
            storage_uri=data.get("storage_uri"),
            storage_url=data.get("storage_url"),
            status=data.get("status"),
            status_message=data.get("status_message"),
            processing_strategy=processing_strategy,
            hits=data.get("hits", 0),
            source=data.get("source"),
            chunk_count=data.get("chunk_count"),
            chunks=data.get("chunks"),
            metadata=metadata,
            created_at=self._parse_datetime(data.get("created_at")),
            updated_at=self._parse_datetime(data.get("updated_at")),
            processed_at=self._parse_datetime(data.get("processed_at"))
        )
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None


class SupabaseDocumentChunkRepository(DocumentChunkRepositoryInterface):
    """Supabase implementation of document chunk repository"""
    
    def __init__(self, db_service: DatabaseService):
        self.db = db_service
    
    async def create_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Create document chunks"""
        
        chunk_data = []
        for chunk in chunks:
            data = {
                "id": chunk.id,
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding": chunk.embedding,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char,
                "created_at": chunk.created_at.isoformat() if chunk.created_at else datetime.utcnow().isoformat()
            }
            chunk_data.append(data)
        
        results = await self.db.create_document_chunks(chunk_data)
        return [self._map_to_chunk(result) for result in results]
    
    async def get_chunks_by_document_id(self, document_id: str) -> List[DocumentChunk]:
        """Get all chunks for a document"""
        
        results = await self.db.get_document_chunks(document_id)
        return [self._map_to_chunk(result) for result in results]
    
    async def delete_chunks_by_document_id(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        
        return await self.db.delete_document_chunks(document_id)
    
    async def search_chunks(self, query: str, user_id: str, limit: int = 10) -> List[DocumentChunk]:
        """Search chunks by content (for RAG implementation)"""
        
        # For now, simple text search - would be enhanced with vector search later
        results = await self.db.search_document_chunks_by_content(query, user_id, limit)
        return [self._map_to_chunk(result) for result in results]
    
    def _map_to_chunk(self, data: Dict[str, Any]) -> DocumentChunk:
        """Map database row to DocumentChunk entity"""
        
        metadata = data.get("metadata", {})
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        return DocumentChunk(
            id=data.get("id"),
            document_id=data.get("document_id"),
            chunk_index=data.get("chunk_index"),
            content=data.get("content"),
            metadata=metadata,
            embedding=data.get("embedding"),
            start_char=data.get("start_char"),
            end_char=data.get("end_char"),
            created_at=self._parse_datetime(data.get("created_at"))
        )
    
    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None
        try:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return None