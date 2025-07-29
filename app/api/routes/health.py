"""
Health check endpoints
"""

from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Service health check"""
    return {
        "status": "healthy",
        "service": "NotebookBobu API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "llamacloud_configured": bool(settings.LLAMACLOUD_API_KEY)
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}