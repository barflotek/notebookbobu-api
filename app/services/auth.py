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
    This should integrate with your inbox-zero auth system
    """
    
    # For development/testing - use a fixed user ID
    if settings.ENVIRONMENT == "development":
        return "test-user-123"
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        # Extract Bearer token
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid authorization format")
        
        token = authorization.split(" ")[1]
        
        # Decode JWT token (adjust based on your auth system)
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
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