"""
NotebookBobu API Service
Production-ready FastAPI service for document processing and AI analysis
"""

from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import time

from app.api.routes import documents, chat, health, documents_v2, auth
from app.core.config import settings
from app.middleware.api_key_auth import api_key_auth


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    print("🚀 NotebookBobu API Service starting...")
    print(f"📍 Environment: {settings.ENVIRONMENT}")
    print(f"🔗 Supabase URL: {settings.SUPABASE_URL}")
    yield
    print("🛑 NotebookBobu API Service shutting down...")


# Create FastAPI app
app = FastAPI(
    title="NotebookBobu API",
    description="Document processing and AI analysis service for inbox-zero",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API key authentication
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(
    documents.router, 
    prefix="/api", 
    tags=["documents"],
    dependencies=[Depends(api_key_auth)]
)
app.include_router(
    documents_v2.router, 
    prefix="/api", 
    tags=["documents-v2"],
    dependencies=[Depends(api_key_auth)]
)
app.include_router(
    chat.router, 
    prefix="/api", 
    tags=["chat"],
    dependencies=[Depends(api_key_auth)]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "NotebookBobu API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/api/health"
    }


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for debugging"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")
    
    return response


# For Vercel
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


