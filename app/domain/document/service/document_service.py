"""
Document service implementation following Coze Studio patterns
"""

import uuid
from typing import List, Optional, BinaryIO
from datetime import datetime

from app.domain.document.entity import Document, DocumentChunk, DocumentType, DocumentStatus, DocumentSource
from app.domain.document.repository import DocumentRepositoryInterface, DocumentChunkRepositoryInterface
from app.services.document_processor import DocumentProcessor


class DocumentServiceInterface:
    """Document service interface"""
    
    async def create_document_from_upload(
        self, 
        file: BinaryIO, 
        filename: str, 
        title: str, 
        user_id: str
    ) -> Document:
        """Create document from file upload"""
        pass
    
    async def process_document(self, document_id: str) -> Document:
        """Process document and create chunks"""
        pass
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get document by ID"""
        pass
    
    async def list_documents(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Document]:
        """List user documents"""
        pass
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document and related chunks"""
        pass


class DocumentService(DocumentServiceInterface):
    """Document service implementation"""
    
    def __init__(
        self,
        document_repo: DocumentRepositoryInterface,
        chunk_repo: DocumentChunkRepositoryInterface,
        processor: DocumentProcessor
    ):
        self.document_repo = document_repo
        self.chunk_repo = chunk_repo
        self.processor = processor
    
    async def create_document_from_upload(
        self, 
        file: BinaryIO, 
        filename: str, 
        title: str, 
        user_id: str
    ) -> Document:
        """Create document from file upload with proper metadata"""
        
        # Read file content
        content = file.read()
        file_size = len(content)
        
        # Determine document type from filename
        file_extension = filename.split('.')[-1].lower()
        doc_type = self._get_document_type(file_extension)
        
        # Create document entity
        document = Document(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            type=doc_type,
            file_extension=file_extension,
            size=file_size,
            status=DocumentStatus.UPLOADED,
            source=DocumentSource.UPLOAD,
            created_at=datetime.utcnow()
        )
        
        # Store raw content if text-based
        if doc_type in [DocumentType.TEXT, DocumentType.MARKDOWN]:
            try:
                document.raw_content = content.decode('utf-8')
                document.char_count = len(document.raw_content)
            except UnicodeDecodeError:
                document.status = DocumentStatus.FAILED
                document.status_message = "Failed to decode text content"
        
        # Save to repository
        return await self.document_repo.create_document(document)
    
    async def process_document(self, document_id: str) -> Document:
        """Process document using NotebookLlama or mock processor"""
        
        # Get document
        document = await self.document_repo.get_document_by_id(document_id, None)  # Admin access
        if not document:
            raise ValueError(f"Document {document_id} not found")
        
        # Update status to processing
        await self.document_repo.update_document_status(
            document_id, 
            DocumentStatus.PROCESSING.value,
            "Processing document content"
        )
        
        try:
            # Process with NotebookLlama or mock
            if document.raw_content:
                processing_result = await self.processor.process_text(
                    text=document.raw_content,
                    title=document.title
                )
            else:
                # For PDF/DOCX, would need file processing
                processing_result = {
                    "summary": f"Mock summary for {document.title}",
                    "key_points": ["Point 1", "Point 2", "Point 3"],
                    "chunks": self._create_mock_chunks(document.raw_content or "No content", document.id)
                }
            
            # Create chunks
            chunks = []
            for i, chunk_data in enumerate(processing_result.get("chunks", [])):
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document.id,
                    chunk_index=i,
                    content=chunk_data.get("content", ""),
                    metadata=chunk_data.get("metadata", {}),
                    created_at=datetime.utcnow()
                )
                chunks.append(chunk)
            
            # Save chunks
            if chunks:
                await self.chunk_repo.create_chunks(chunks)
            
            # Update document with processing results
            document.processed_content = processing_result.get("summary", "")
            document.chunk_count = len(chunks)
            document.status = DocumentStatus.PROCESSED
            document.status_message = "Successfully processed"
            document.processed_at = datetime.utcnow()
            document.metadata.update({
                "key_points": processing_result.get("key_points", []),
                "processing_time": datetime.utcnow().isoformat()
            })
            
            return await self.document_repo.update_document(document)
            
        except Exception as e:
            # Handle processing errors
            await self.document_repo.update_document_status(
                document_id,
                DocumentStatus.FAILED.value,
                f"Processing failed: {str(e)}"
            )
            raise
    
    async def get_document(self, document_id: str, user_id: str) -> Optional[Document]:
        """Get document with user ownership check"""
        return await self.document_repo.get_document_by_id(document_id, user_id)
    
    async def list_documents(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Document]:
        """List user documents with pagination"""
        return await self.document_repo.get_documents_by_user(user_id, limit, offset)
    
    async def delete_document(self, document_id: str, user_id: str) -> bool:
        """Delete document and all related chunks"""
        # Delete chunks first
        await self.chunk_repo.delete_chunks_by_document_id(document_id)
        
        # Delete document
        return await self.document_repo.delete_document(document_id, user_id)
    
    def _get_document_type(self, file_extension: str) -> DocumentType:
        """Map file extension to document type"""
        extension_map = {
            'pdf': DocumentType.PDF,
            'txt': DocumentType.TEXT,
            'md': DocumentType.MARKDOWN,
            'docx': DocumentType.DOCX
        }
        return extension_map.get(file_extension.lower(), DocumentType.TEXT)
    
    def _create_mock_chunks(self, content: str, document_id: str) -> List[dict]:
        """Create mock chunks for testing"""
        if not content:
            return []
        
        chunk_size = 500
        chunks = []
        
        for i in range(0, len(content), chunk_size):
            chunk_content = content[i:i + chunk_size]
            chunks.append({
                "content": chunk_content,
                "metadata": {
                    "start_char": i,
                    "end_char": min(i + chunk_size, len(content)),
                    "chunk_type": "text"
                }
            })
        
        return chunks