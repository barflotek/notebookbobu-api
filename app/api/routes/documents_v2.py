"""
Domain-driven document processing endpoints following Coze Studio patterns
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import List, Optional
import uuid
from io import BytesIO

from app.core.container import container
from app.services.auth import get_current_user
from app.domain.document.entity import Document, DocumentStatus
from app.models.documents import DocumentResponse, DocumentProcessResponse


router = APIRouter()


@router.post("/v2/process", response_model=DocumentProcessResponse)
async def process_document_v2(
    file: UploadFile = File(...),
    title: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    """
    Process a document using domain-driven architecture
    
    This endpoint:
    1. Creates a Document entity
    2. Stores it via repository
    3. Processes it via domain service
    4. Returns structured response
    """
    
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.md', '.docx'}
    file_extension = '.' + file.filename.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Read file content
        content = await file.read()
        file_io = BytesIO(content)
        
        # Create document using domain service
        document_service = container.document_service
        document = await document_service.create_document_from_upload(
            file=file_io,
            filename=file.filename,
            title=title,
            user_id=user_id
        )
        
        # Process document
        processed_document = await document_service.process_document(document.id)
        
        return DocumentProcessResponse(
            document_id=processed_document.id,
            title=processed_document.title,
            status=processed_document.status.value,
            summary=processed_document.processed_content or "Processing completed",
            key_points=processed_document.metadata.get("key_points", []),
            chunk_count=processed_document.chunk_count or 0,
            file_size=processed_document.size,
            processing_time=processed_document.metadata.get("processing_time")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/v2/documents", response_model=List[DocumentResponse])
async def list_documents_v2(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user)
):
    """
    List user documents with pagination using domain service
    """
    
    try:
        document_service = container.document_service
        documents = await document_service.list_documents(user_id, limit, offset)
        
        return [
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                type=doc.type.value,
                status=doc.status.value,
                size=doc.size,
                chunk_count=doc.chunk_count or 0,
                hits=doc.hits,
                created_at=doc.created_at.isoformat() if doc.created_at else None,
                updated_at=doc.updated_at.isoformat() if doc.updated_at else None
            )
            for doc in documents
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")


@router.get("/v2/documents/{document_id}", response_model=DocumentResponse)
async def get_document_v2(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get specific document using domain service
    """
    
    try:
        document_service = container.document_service
        document = await document_service.get_document(document_id, user_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return DocumentResponse(
            id=document.id,
            title=document.title,
            type=document.type.value,
            status=document.status.value,
            size=document.size,
            chunk_count=document.chunk_count or 0,
            hits=document.hits,
            summary=document.processed_content,
            metadata=document.metadata,
            created_at=document.created_at.isoformat() if document.created_at else None,
            updated_at=document.updated_at.isoformat() if document.updated_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")


@router.delete("/v2/documents/{document_id}")
async def delete_document_v2(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete document using domain service
    """
    
    try:
        document_service = container.document_service
        success = await document_service.delete_document(document_id, user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@router.get("/v2/documents/{document_id}/chunks")
async def get_document_chunks_v2(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get document chunks for RAG or detailed analysis
    """
    
    try:
        # Verify document ownership first
        document_service = container.document_service
        document = await document_service.get_document(document_id, user_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Get chunks via repository
        chunk_repo = container.chunk_repository
        chunks = await chunk_repo.get_chunks_by_document_id(document_id)
        
        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "chunks": [
                {
                    "id": chunk.id,
                    "index": chunk.chunk_index,
                    "content": chunk.content,
                    "metadata": chunk.metadata
                }
                for chunk in chunks
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chunks: {str(e)}")


@router.get("/v2/search")
async def search_documents_v2(
    query: str,
    limit: int = 10,
    user_id: str = Depends(get_current_user)
):
    """
    Search document chunks for RAG implementation
    """
    
    if not query or len(query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters")
    
    try:
        chunk_repo = container.chunk_repository
        chunks = await chunk_repo.search_chunks(query, user_id, limit)
        
        return {
            "query": query,
            "results": [
                {
                    "chunk_id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "relevance_score": 1.0  # Would be calculated with proper vector search
                }
                for chunk in chunks
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")