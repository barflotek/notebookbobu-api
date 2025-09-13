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
        "llamacloud_configured": bool(settings.LLAMACLOUD_API_KEY),
        "api_keys": {
            "main_api_key": settings.API_KEY[:8] + "..." if settings.API_KEY else "NOT SET",
            "inbox_api_key": settings.INBOX_ZERO_API_KEY[:8] + "..." if settings.INBOX_ZERO_API_KEY else "NOT SET",
            "main_configured": bool(settings.API_KEY and len(settings.API_KEY) > 0),
            "inbox_configured": bool(settings.INBOX_ZERO_API_KEY and len(settings.INBOX_ZERO_API_KEY) > 0)
        }
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "pong"}


@router.get("/test-auth")
async def test_auth():
    """Test endpoint to validate API key manually"""
    # Check raw environment values
    import os
    from app.core.config import settings
    
    raw_api_key = os.getenv("API_KEY", "NOT_SET")
    raw_inbox_key = os.getenv("INBOX_ZERO_API_KEY", "NOT_SET")
    
    return {
        "raw_api_key": repr(raw_api_key),
        "raw_inbox_key": repr(raw_inbox_key),
        "settings_api_key": repr(settings.API_KEY),
        "settings_inbox_key": repr(settings.INBOX_ZERO_API_KEY),
        "test_keys": [
            "nb-general-api-key-2024",
            "inbox-zero-api-key-2024"
        ]
    }