"""
Chat and query endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from app.models.chat import QueryRequest, QueryResponse, ChatHistoryResponse
from app.services.auth import get_current_user
from app.services.chat_service import ChatService
from app.services.database import DatabaseService

router = APIRouter()
chat_service = ChatService()
db_service = DatabaseService()


@router.post("/query", response_model=QueryResponse)
async def query_documents(
    request: QueryRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Query processed documents with natural language
    """
    try:
        # Get user's documents
        if request.document_ids:
            documents = await db_service.get_documents_by_ids(
                document_ids=request.document_ids,
                user_id=user_id
            )
        else:
            # Query all user documents if no specific IDs provided
            documents = await db_service.get_user_documents(user_id=user_id)
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found to query")
        
        # Process query
        result = await chat_service.query_documents(
            question=request.question,
            documents=documents,
            user_id=user_id
        )
        
        # Store chat history
        await db_service.store_chat(
            user_id=user_id,
            document_ids=[doc["id"] for doc in documents],
            question=request.question,
            answer=result["answer"],
            sources=result.get("sources", [])
        )
        
        return QueryResponse(
            success=True,
            answer=result["answer"],
            sources=result.get("sources", []),
            document_count=len(documents)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/chat-history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    user_id: str = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """
    Get user's chat history
    """
    try:
        history = await db_service.get_chat_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch chat history: {str(e)}")


@router.post("/podcast")
async def generate_podcast(
    document_ids: List[str],
    user_id: str = Depends(get_current_user),
    title: Optional[str] = None,
    voice_settings: Optional[dict] = None
):
    """
    Generate a podcast from selected documents
    """
    try:
        # Get documents
        documents = await db_service.get_documents_by_ids(
            document_ids=document_ids,
            user_id=user_id
        )
        
        if not documents:
            raise HTTPException(status_code=404, detail="No documents found")
        
        # Generate podcast (this would integrate with ElevenLabs or similar)
        result = await chat_service.generate_podcast(
            documents=documents,
            title=title or f"Podcast from {len(documents)} documents",
            voice_settings=voice_settings
        )
        
        return {
            "success": True,
            "podcast_id": result["podcast_id"],
            "title": result["title"],
            "transcript": result.get("transcript"),
            "audio_url": result.get("audio_url"),
            "status": "generating"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Podcast generation failed: {str(e)}")