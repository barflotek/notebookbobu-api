"""
Behavioral Tracking Middleware - Automatically tracks user interactions for intelligence system
"""
import time
import asyncio
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.services.intelligence_sync import intelligence_sync

logger = logging.getLogger(__name__)

class BehavioralTrackingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically track user behavioral data for the intelligence system.
    
    Tracks:
    - API endpoint usage patterns
    - Document processing frequency
    - Response times and engagement
    - Error patterns
    """
    
    def __init__(self, app, track_paths: list = None):
        super().__init__(app)
        self.track_paths = track_paths or [
            "/api/v2/documents/",
            "/api/clients/",
            "/api/v2/documents/process",
            "/api/v2/documents/analyze"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip tracking for health checks and non-API paths
        if request.url.path in ["/health", "/api/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Check if this is a trackable path
        should_track = any(path in request.url.path for path in self.track_paths)
        
        if not should_track:
            return await call_next(request)
        
        # Start timing
        start_time = time.time()
        user_id = None
        
        try:
            # Try to extract user ID from various sources
            user_id = await self.extract_user_id(request)
            
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Track the interaction asynchronously (don't wait for it)
            if user_id and response.status_code < 400:
                asyncio.create_task(
                    self.track_successful_interaction(
                        request, response, user_id, processing_time
                    )
                )
            
            return response
            
        except Exception as e:
            # Track errors too
            processing_time = time.time() - start_time
            if user_id:
                asyncio.create_task(
                    self.track_error_interaction(request, user_id, str(e), processing_time)
                )
            raise
    
    async def extract_user_id(self, request: Request) -> str:
        """Extract user ID from request (header, token, path param, etc.)"""
        try:
            # Check for user ID in headers
            user_id = request.headers.get("x-user-id")
            if user_id:
                return user_id
            
            # Check for client ID in path parameters
            if "client_id" in request.path_params:
                return request.path_params["client_id"]
            
            # Check for user ID in path parameters
            if "user_id" in request.path_params:
                return request.path_params["user_id"]
            
            # Try to extract from query parameters
            user_id = request.query_params.get("user_id")
            if user_id:
                return user_id
            
            # For document processing, try to extract from request body
            if request.method == "POST" and "documents" in request.url.path:
                # This would require reading the body, which we'll skip for now
                # to avoid interfering with the main request processing
                pass
            
            return None
            
        except Exception as e:
            logger.warning(f"Error extracting user ID: {str(e)}")
            return None
    
    async def track_successful_interaction(
        self, 
        request: Request, 
        response: Response, 
        user_id: str, 
        processing_time: float
    ):
        """Track successful API interactions"""
        try:
            interaction_type = self.determine_interaction_type(request.url.path, request.method)
            
            interaction_data = {
                "id": f"interaction_{int(time.time())}",
                "type": interaction_type,
                "user_id": user_id,
                "endpoint": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            
            # Update engagement score based on interaction type
            score_delta = self.calculate_engagement_delta(interaction_type, processing_time)
            
            # Track both the interaction and update the score
            await intelligence_sync.track_document_interaction(interaction_data, user_id)
            if score_delta != 0:
                await intelligence_sync.update_engagement_score(user_id, score_delta)
                
        except Exception as e:
            logger.error(f"Error tracking successful interaction: {str(e)}")
    
    async def track_error_interaction(
        self, 
        request: Request, 
        user_id: str, 
        error: str, 
        processing_time: float
    ):
        """Track failed interactions for behavioral analysis"""
        try:
            interaction_data = {
                "id": f"error_{int(time.time())}",
                "type": "error",
                "user_id": user_id,
                "endpoint": request.url.path,
                "method": request.method,
                "error": error,
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            
            await intelligence_sync.track_document_interaction(interaction_data, user_id)
            # Decrease engagement score for errors
            await intelligence_sync.update_engagement_score(user_id, -2)
            
        except Exception as e:
            logger.error(f"Error tracking failed interaction: {str(e)}")
    
    def determine_interaction_type(self, path: str, method: str) -> str:
        """Determine the type of interaction based on the API endpoint"""
        if "documents/process" in path:
            return "document_processing"
        elif "documents/analyze" in path:
            return "document_analysis"
        elif "documents" in path and method == "POST":
            return "document_upload"
        elif "documents" in path and method == "GET":
            return "document_retrieval"
        elif "clients" in path and method == "POST":
            return "client_creation"
        elif "clients" in path and method == "GET":
            return "client_lookup"
        else:
            return "api_interaction"
    
    def calculate_engagement_delta(self, interaction_type: str, processing_time: float) -> int:
        """Calculate how much to adjust engagement score based on interaction"""
        base_scores = {
            "document_processing": 8,
            "document_analysis": 6,
            "document_upload": 5,
            "document_retrieval": 2,
            "client_creation": 10,
            "client_lookup": 1,
            "api_interaction": 1
        }
        
        base_score = base_scores.get(interaction_type, 1)
        
        # Bonus for quick processing (under 2 seconds)
        if processing_time < 2.0:
            base_score += 1
        # Penalty for very slow processing (over 10 seconds)
        elif processing_time > 10.0:
            base_score -= 2
        
        return max(0, base_score)