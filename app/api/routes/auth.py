"""
Authentication and API key management endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from app.middleware.api_key_auth import generate_api_key, get_example_keys, api_key_auth
from app.core.config import settings

router = APIRouter()


@router.get("/api-keys/examples")
async def get_example_api_keys():
    """
    Get example API keys for development and testing
    PUBLIC ENDPOINT - No authentication required
    """
    
    # Only show examples in development
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")
    
    examples = get_example_keys()
    
    return {
        "message": "Example API keys for development",
        "note": "These are examples - generate your own for production",
        "examples": examples,
        "usage": {
            "header": "Authorization: Bearer YOUR_API_KEY",
            "curl_example": f"curl -H 'Authorization: Bearer {examples['general']}' https://your-api.vercel.app/api/health"
        }
    }


@router.post("/api-keys/generate")
async def generate_new_api_key(
    prefix: str = "nb",
    api_key: str = Depends(api_key_auth)
):
    """
    Generate a new API key
    PROTECTED ENDPOINT - Requires existing API key
    """
    
    new_key = generate_api_key(prefix)
    
    return {
        "message": "New API key generated",
        "api_key": new_key,
        "prefix": prefix,
        "note": "Store this key securely - it won't be shown again"
    }


@router.get("/validate")
async def validate_api_key(api_key: str = Depends(api_key_auth)):
    """
    Validate current API key
    PROTECTED ENDPOINT - Test your API key
    """
    
    return {
        "message": "API key is valid",
        "authenticated": True,
        "key_prefix": api_key[:8] + "..." if len(api_key) > 8 else api_key
    }