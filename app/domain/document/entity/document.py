"""
Document domain entity following Coze Studio patterns
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class DocumentType(str, Enum):
    """Document type enumeration"""
    PDF = "pdf"
    TEXT = "txt"
    MARKDOWN = "md"
    DOCX = "docx"


class DocumentStatus(str, Enum):
    """Document processing status"""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class DocumentSource(str, Enum):
    """Document source"""
    UPLOAD = "upload"
    URL = "url"
    API = "api"


class ProcessingStrategy(BaseModel):
    """Document processing strategy"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    extract_images: bool = False
    extract_tables: bool = True


class Document(BaseModel):
    """Document entity with comprehensive metadata"""
    
    # Core identification
    id: Optional[str] = None
    user_id: str
    title: str
    
    # Document metadata
    type: DocumentType
    file_extension: str
    size: int
    char_count: Optional[int] = None
    
    # Content and storage
    raw_content: Optional[str] = None
    processed_content: Optional[str] = None
    storage_uri: Optional[str] = None
    storage_url: Optional[str] = None
    
    # Processing
    status: DocumentStatus = DocumentStatus.UPLOADED
    status_message: Optional[str] = None
    processing_strategy: ProcessingStrategy = ProcessingStrategy()
    
    # Analytics
    hits: int = 0
    source: DocumentSource = DocumentSource.UPLOAD
    
    # Chunking results
    chunk_count: Optional[int] = None
    chunks: Optional[Dict[str, Any]] = None
    
    # Client relationship (CRM integration)
    client_id: Optional[str] = None  # Link to client entity
    client_context: Optional[str] = None  # "email_attachment", "manual_upload", "analysis_request"
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    processed_at: Optional[datetime] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = {}

    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class DocumentChunk(BaseModel):
    """Document chunk entity"""
    
    id: Optional[str] = None
    document_id: str
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = {}
    
    # Vector embeddings (for future RAG implementation)
    embedding: Optional[list] = None
    
    # Chunk boundaries
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    
    # Timestamps
    created_at: Optional[datetime] = None

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }