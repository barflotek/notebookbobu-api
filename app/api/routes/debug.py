"""
Debug endpoints for API key testing
"""

from fastapi import APIRouter, Depends
from app.core.config import settings
from app.middleware.api_key_auth import api_key_auth

router = APIRouter()


@router.get("/debug/api-keys")
async def debug_api_keys():
    """
    Debug endpoint to check configured API keys
    PUBLIC ENDPOINT - Only in development
    """
    
    if settings.ENVIRONMENT != "development":
        return {"error": "Debug endpoints only available in development"}
    
    return {
        "environment": settings.ENVIRONMENT,
        "configured_keys": {
            "API_KEY": settings.API_KEY[:16] + "..." if settings.API_KEY else "NOT SET",
            "INBOX_ZERO_API_KEY": settings.INBOX_ZERO_API_KEY[:16] + "..." if settings.INBOX_ZERO_API_KEY else "NOT SET",
        },
        "note": "Only showing first 16 characters for security"
    }


@router.get("/debug/config")
async def debug_config():
    """Debug configuration"""
    
    if settings.ENVIRONMENT != "development":
        return {"error": "Debug endpoints only available in development"}
    
    return {
        "environment": settings.ENVIRONMENT,
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "api_keys_configured": bool(settings.API_KEY or settings.INBOX_ZERO_API_KEY)
    }


@router.get("/debug/auth-test")
async def test_auth_endpoint(api_key: str = Depends(api_key_auth)):
    """
    Test endpoint to verify API key authentication works
    PROTECTED ENDPOINT - Requires valid API key
    """
    
    return {
        "message": "Authentication successful! Your API key is valid.",
        "authenticated": True,
        "api_key_prefix": api_key[:16] + "..." if len(api_key) > 16 else api_key,
        "environment": settings.ENVIRONMENT
    }