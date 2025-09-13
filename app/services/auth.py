"""
Authentication service
"""

from fastapi import HTTPException, Header, Depends
from typing import Optional
import jwt
from app.core.config import settings


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """
    Extract user ID from authorization header
    Updated to work with API key authentication instead of JWT
    """
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract Bearer token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.split(" ")[1]
        
        # Validate API key
        valid_keys = [
            settings.API_KEY.strip() if settings.API_KEY else "",
            settings.INBOX_ZERO_API_KEY.strip() if settings.INBOX_ZERO_API_KEY else "",
        ]
        valid_keys = [key for key in valid_keys if key and key.strip()]
        
        if not valid_keys:
            raise HTTPException(status_code=401, detail="No API keys configured")
        
        # Check if token matches any valid API key
        import secrets
        for valid_key in valid_keys:
            if secrets.compare_digest(token, valid_key):
                # Return a user ID based on which API key was used
                if token == settings.INBOX_ZERO_API_KEY.strip():
                    return "inbox-zero-user"
                else:
                    return "api-user"
        
        raise HTTPException(status_code=401, detail="Invalid API key")
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")


async def verify_api_key(api_key: Optional[str] = Header(None, alias="X-API-Key")) -> bool:
    """
    Verify internal API key for service-to-service communication
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True