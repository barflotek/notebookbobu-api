"""
API Key Authentication Middleware
"""

from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import secrets
import hashlib

from app.core.config import settings


class APIKeyAuth(HTTPBearer):
    """API Key authentication using Bearer token"""
    
    def __init__(self, auto_error: bool = True):
        super(APIKeyAuth, self).__init__(auto_error=auto_error)
    
    async def __call__(self, request: Request) -> Optional[str]:
        """Validate API key from Authorization header"""
        
        # Skip authentication for health and docs endpoints
        if request.url.path in ["/", "/api/health", "/api/ping", "/docs", "/redoc", "/openapi.json"]:
            return "public"
        
        # Get authorization header
        authorization: HTTPAuthorizationCredentials = await super(APIKeyAuth, self).__call__(request)
        
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate API key
        if not self._validate_api_key(authorization.credentials):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return authorization.credentials
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key"""
        
        # Check against configured API keys
        valid_keys = [
            settings.API_KEY,  # Main API key from config
            settings.INBOX_ZERO_API_KEY,  # Specific key for inbox-zero (if set)
        ]
        
        # Remove None values
        valid_keys = [key for key in valid_keys if key]
        
        if not valid_keys:
            # If no API keys configured, reject all requests
            return False
        
        # Use secure comparison to prevent timing attacks
        for valid_key in valid_keys:
            if secrets.compare_digest(api_key, valid_key):
                return True
        
        return False


# Create global instance
api_key_auth = APIKeyAuth()


def generate_api_key(prefix: str = "nb") -> str:
    """Generate a secure API key"""
    random_bytes = secrets.token_bytes(32)
    key_hash = hashlib.sha256(random_bytes).hexdigest()[:32]
    return f"{prefix}_{key_hash}"


# Example API keys for different clients
def get_example_keys():
    """Generate example API keys for different services"""
    return {
        "inbox_zero": generate_api_key("inbox"),
        "general": generate_api_key("nb"),
        "development": generate_api_key("dev")
    }