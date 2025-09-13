"""
Application configuration settings
"""

import os
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").strip()
    
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "NotebookBobu API"
    
    # Security
    JWT_SECRET: str = os.getenv("JWT_SECRET", "your-super-secret-jwt-key").strip()
    API_KEY: str = os.getenv("API_KEY", "your-internal-api-key").strip()
    INBOX_ZERO_API_KEY: str = os.getenv("INBOX_ZERO_API_KEY", "").strip()  # Specific key for inbox-zero
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000").strip()
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://*.vercel.app",
        "https://*.netlify.app",
        os.getenv("FRONTEND_URL", "")
    ]
    
    # Database
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    
    # AI Services
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLAMACLOUD_API_KEY: str = os.getenv("LLAMACLOUD_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    
    # Processing Settings
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    SUPPORTED_FILE_TYPES: List[str] = [".pdf", ".txt", ".md", ".docx"]
    
    # Database Tables
    DOCUMENTS_TABLE: str = "notebookbobu_documents"
    CHATS_TABLE: str = "notebookbobu_chats"
    PODCASTS_TABLE: str = "notebookbobu_podcasts"
    STORAGE_BUCKET: str = "documents"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()