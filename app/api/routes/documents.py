"""
Document processing endpoints
"""

from fastapi import APIRouter, File, UploadFile, Form, HTTPException, Depends
from typing import List, Optional
import uuid
import tempfile
import os
from pathlib import Path

from app.core.config import settings
from app.models.documents import DocumentResponse, DocumentProcessResponse
from app.services.auth import get_current_user
from app.services.document_processor import DocumentProcessor
from app.services.database import DatabaseService

router = APIRouter()
doc_processor = DocumentProcessor()
db_service = DatabaseService()


@router.post("/process", response_model=DocumentProcessResponse)
async def process_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    user_id: str = Depends(get_current_user)
):
    """
    Process a document (PDF, TXT, MD) and extract insights
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.SUPPORTED_FILE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Supported: {settings.SUPPORTED_FILE_TYPES}"
            )
        
        # Check file size
        content = await file.read()
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / (1024*1024):.1f}MB"
            )
        
        # Process document
        document_id = str(uuid.uuid4())
        
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Process with NotebookBobu (using NotebookLlama under the hood)
            result = await doc_processor.process_document(
                file_path=tmp_path,
                title=title,
                document_id=document_id
            )
            
            # Store in database
            await db_service.store_document(
                document_id=document_id,
                user_id=user_id,
                title=title,
                content=content,
                summary=result.get("summary"),
                bullet_points=result.get("bullet_points"),
                q_and_a=result.get("q_and_a"),
                mindmap_html=result.get("mindmap_html")
            )
            
            return DocumentProcessResponse(
                success=True,
                document_id=document_id,
                summary=result.get("summary"),
                bullet_points=result.get("bullet_points"),
                q_and_a=result.get("q_and_a"),
                mindmap_html=result.get("mindmap_html")
            )
            
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    user_id: str = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    List user's processed documents
    """
    try:
        documents = await db_service.get_user_documents(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch documents: {str(e)}")


@router.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get a specific document by ID
    """
    try:
        document = await db_service.get_document(document_id, user_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch document: {str(e)}")


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a document
    """
    try:
        success = await db_service.delete_document(document_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"success": True, "message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")