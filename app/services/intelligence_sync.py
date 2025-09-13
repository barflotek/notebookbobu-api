"""
Intelligence Sync Service - Connects NotebookBobu with Client Intelligence System
"""
import httpx
import json
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

class IntelligenceSyncService:
    def __init__(self):
        self.client_intelligence_url = "https://client-intelligence-system-nqjqq6nua-sentinel-io.vercel.app"
        self.api_key = settings.NOTEBOOKBOBU_API_KEY
        
    async def sync_client_profile(self, client_data: Dict[str, Any]) -> bool:
        """Sync client profile to intelligence system"""
        try:
            payload_data = {
                "name": client_data.get("name"),
                "email": client_data.get("email"),
                "phone": client_data.get("phone"),
                "businessOwner": client_data.get("user_id"),
                "clientId": client_data.get("id"),
                "status": "active",
                "preferences": {
                    "communicationChannel": ["email"],
                    "timezone": "UTC"
                },
                "intelligenceScores": {
                    "engagementScore": 50,  # Default starting score
                    "lastUpdated": datetime.utcnow().isoformat()
                },
                "firstInteraction": client_data.get("created_at", datetime.utcnow().isoformat()),
                "lastInteraction": datetime.utcnow().isoformat()
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.client_intelligence_url}/api/client-profiles",
                    json=payload_data,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully synced client profile: {client_data.get('id')}")
                    return True
                else:
                    logger.warning(f"Failed to sync client profile: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error syncing client profile: {str(e)}")
            return False
    
    async def track_document_interaction(self, document_data: Dict[str, Any], user_id: str) -> bool:
        """Track document processing as behavioral data"""
        try:
            interaction_data = {
                "type": "document_processing",
                "clientId": user_id,
                "metadata": {
                    "document_id": document_data.get("id"),
                    "document_title": document_data.get("title", "Unknown"),
                    "document_type": document_data.get("content_type", "unknown"),
                    "processing_time": document_data.get("processing_time", 0),
                    "ai_confidence": document_data.get("ai_confidence_score", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.client_intelligence_url}/api/interactions",
                    json=interaction_data,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Successfully tracked document interaction for user: {user_id}")
                    return True
                else:
                    logger.warning(f"Failed to track interaction: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error tracking document interaction: {str(e)}")
            return False
    
    async def update_engagement_score(self, user_id: str, score_delta: int = 5) -> bool:
        """Update user engagement score based on activity"""
        try:
            # Get current client profile
            async with httpx.AsyncClient() as client:
                # First get the current profile
                get_response = await client.get(
                    f"{self.client_intelligence_url}/api/client-profiles",
                    params={"where[clientId][equals]": user_id},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0
                )
                
                if get_response.status_code == 200:
                    profiles = get_response.json().get("docs", [])
                    if profiles:
                        profile = profiles[0]
                        current_score = profile.get("intelligenceScores", {}).get("engagementScore", 50)
                        new_score = min(100, max(0, current_score + score_delta))
                        
                        # Update the score
                        update_data = {
                            "intelligenceScores": {
                                "engagementScore": new_score,
                                "lastUpdated": datetime.utcnow().isoformat()
                            },
                            "lastInteraction": datetime.utcnow().isoformat()
                        }
                        
                        update_response = await client.patch(
                            f"{self.client_intelligence_url}/api/client-profiles/{profile['id']}",
                            json=update_data,
                            headers={
                                "Content-Type": "application/json",
                                "Authorization": f"Bearer {self.api_key}"
                            },
                            timeout=30.0
                        )
                        
                        if update_response.status_code == 200:
                            logger.info(f"Updated engagement score for {user_id}: {current_score} -> {new_score}")
                            return True
                
                logger.warning(f"Could not update engagement score for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating engagement score: {str(e)}")
            return False
    
    async def get_client_intelligence(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get client intelligence data for recommendations"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.client_intelligence_url}/api/client-profiles",
                    params={"where[clientId][equals]": user_id},
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    profiles = response.json().get("docs", [])
                    if profiles:
                        return profiles[0]
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting client intelligence: {str(e)}")
            return None

# Global instance
intelligence_sync = IntelligenceSyncService()