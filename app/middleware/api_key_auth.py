"""
API Key Authentication Middleware
"""

from fastapi import HTTPException, status, Request
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional
import secrets
import hashlib

from app.core.config import settings


class APIKeyAuth(SecurityBase):
    """API Key authentication using Bearer token - clean implementation without HTTPBearer conflicts"""
    
    def __init__(self, auto_error: bool = True):
        self.auto_error = auto_error
        self.scheme_name = "Bearer"
    
    async def __call__(self, request: Request) -> Optional[str]:
        """Validate API key from Authorization header"""
        
        # Skip authentication for health and docs endpoints
        public_paths = ["/", "/api/health", "/api/ping", "/api/test-auth", "/docs", "/redoc", "/openapi.json"]
        if request.url.path in public_paths:
            return "public"
        
        # Get authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key required",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        # Parse Bearer token
        scheme, token = get_authorization_scheme_param(authorization)
        if scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization format. Use: Bearer <token>",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        # Validate API key
        if not self._validate_api_key(token):
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid API key",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None
        
        return token
    
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate the provided API key"""
        
        # Debug logging (only in development)
        if settings.ENVIRONMENT == "development":
            print(f"🔍 Received API key: {api_key[:16]}...")
            print(f"🔍 Settings API_KEY: {settings.API_KEY[:16] if settings.API_KEY else 'NOT SET'}...")
            print(f"🔍 Settings INBOX_ZERO_API_KEY: {settings.INBOX_ZERO_API_KEY[:16] if settings.INBOX_ZERO_API_KEY else 'NOT SET'}...")
        
        # Check against configured API keys
        valid_keys = [
            settings.API_KEY.strip() if settings.API_KEY else "",  # Main API key from config
            settings.INBOX_ZERO_API_KEY.strip() if settings.INBOX_ZERO_API_KEY else "",  # Specific key for inbox-zero (if set)
        ]
        
        # Remove None and empty values
        valid_keys = [key for key in valid_keys if key and key.strip()]
        
        if settings.ENVIRONMENT == "development":
            print(f"🔍 Valid keys count: {len(valid_keys)}")
        
        if not valid_keys:
            # If no API keys configured, reject all requests
            if settings.ENVIRONMENT == "development":
                print("❌ No valid keys configured")
            return False
        
        # Use secure comparison to prevent timing attacks
        for i, valid_key in enumerate(valid_keys):
            if settings.ENVIRONMENT == "development":
                print(f"🔍 Comparing against key {i+1}: {valid_key[:16]}...")
            
            if secrets.compare_digest(api_key, valid_key):
                if settings.ENVIRONMENT == "development":
                    print("✅ API key validated successfully")
                return True
        
        if settings.ENVIRONMENT == "development":
            print("❌ API key validation failed")
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