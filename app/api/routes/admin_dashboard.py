"""
Admin Dashboard Routes - Visual interface for Client Intelligence System
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx
from typing import Dict, Any
import logging

from app.services.auth import get_current_user
from app.services.intelligence_sync import intelligence_sync

logger = logging.getLogger(__name__)
router = APIRouter()

# Templates directory (we'll create simple HTML templates)
templates = Jinja2Templates(directory="app/templates")

@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Main admin dashboard - Visual interface for intelligence system"""
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "title": "Client Intelligence Dashboard",
        "api_base": str(request.base_url)
    })

@router.get("/admin/clients", response_class=HTMLResponse)
async def admin_clients(request: Request):
    """Client management interface"""
    return templates.TemplateResponse("admin_clients.html", {
        "request": request,
        "title": "Client Management",
        "api_base": str(request.base_url)
    })

@router.get("/admin/analytics", response_class=HTMLResponse)
async def admin_analytics(request: Request):
    """Analytics dashboard"""
    return templates.TemplateResponse("admin_analytics.html", {
        "request": request,
        "title": "Intelligence Analytics",
        "api_base": str(request.base_url)
    })

# API endpoints for the dashboard
@router.get("/admin/api/dashboard-data")
async def get_dashboard_data(user_id: str = Depends(get_current_user)):
    """Get dashboard data for visual interface"""
    try:
        # Mock dashboard data - in real app, query your database
        dashboard_data = {
            "total_clients": 0,
            "active_clients": 0,
            "avg_engagement_score": 0,
            "recent_interactions": [],
            "top_clients": [],
            "engagement_trends": [],
            "system_health": {
                "api_status": "healthy",
                "db_status": "connected",
                "intelligence_system": "active"
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        return {
            "error": "Unable to load dashboard data",
            "total_clients": 0,
            "active_clients": 0,
            "avg_engagement_score": 0,
            "recent_interactions": [],
            "top_clients": [],
            "engagement_trends": [],
            "system_health": {
                "api_status": "error",
                "db_status": "unknown",
                "intelligence_system": "unknown"
            }
        }

@router.get("/admin/api/clients-data")
async def get_clients_data(user_id: str = Depends(get_current_user)):
    """Get clients data for management interface"""
    try:
        # This would query your actual client database
        # For now, return mock data
        clients_data = {
            "clients": [],
            "total_count": 0,
            "filters": {
                "statuses": ["active", "inactive", "prospect", "former"],
                "risk_levels": ["low", "medium", "high"],
                "engagement_ranges": ["0-25", "26-50", "51-75", "76-100"]
            }
        }
        
        return clients_data
        
    except Exception as e:
        logger.error(f"Error getting clients data: {str(e)}")
        return {"error": str(e), "clients": [], "total_count": 0}

@router.get("/admin/api/intelligence-data")
async def get_intelligence_data(user_id: str = Depends(get_current_user)):
    """Get intelligence analytics data"""
    try:
        # This would aggregate intelligence data from MongoDB
        intelligence_data = {
            "engagement_distribution": {
                "high": 0,
                "medium": 0, 
                "low": 0
            },
            "risk_assessment": {
                "low_risk": 0,
                "medium_risk": 0,
                "high_risk": 0
            },
            "behavioral_trends": [],
            "top_performing_clients": [],
            "alerts": []
        }
        
        return intelligence_data
        
    except Exception as e:
        logger.error(f"Error getting intelligence data: {str(e)}")
        return {"error": str(e)}

@router.post("/admin/api/client/{client_id}/update-score")
async def update_client_score(
    client_id: str, 
    score_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Update client intelligence score"""
    try:
        # Update engagement score via intelligence sync
        new_score = score_data.get("engagement_score", 50)
        success = await intelligence_sync.update_engagement_score(client_id, new_score - 50)
        
        if success:
            return {"success": True, "message": f"Updated score for client {client_id}"}
        else:
            return {"success": False, "message": "Failed to update score"}
            
    except Exception as e:
        logger.error(f"Error updating client score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))