"""
Settings Router — System Configuration
Endpoints: GET /settings, PUT /settings
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
import os
from typing import Optional

router = APIRouter()
log = logging.getLogger(__name__)


class SettingsResponse(BaseModel):
    ollama_model: str
    ollama_base_url: str
    ollama_status: str
    serpapi_configured: bool
    reddit_configured: bool
    google_ads_configured: bool
    database_url: str
    default_country: str = "India"
    default_currency: str = "₹"


class SettingsUpdate(BaseModel):
    ollama_model: Optional[str] = None
    default_country: Optional[str] = None
    default_currency: Optional[str] = None


@router.get("/settings", response_model=SettingsResponse, summary="Get system settings")
async def get_settings():
    """
    Get current system configuration including:
    - Ollama model and status
    - API key configuration status
    - Database settings
    - Default preferences
    """
    try:
        # Check Ollama status
        ollama_status = "unknown"
        try:
            import requests
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            resp = requests.get(f"{ollama_url}/api/tags", timeout=2)
            ollama_status = "online" if resp.ok else "offline"
        except:
            ollama_status = "offline"
        
        return SettingsResponse(
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3:8b"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_status=ollama_status,
            serpapi_configured=bool(os.getenv("SERPAPI_KEY")),
            reddit_configured=bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")),
            google_ads_configured=bool(os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")),
            database_url=os.getenv("DATABASE_URL", "sqlite:///./data/product_intelligence.db"),
            default_country=os.getenv("DEFAULT_COUNTRY", "India"),
            default_currency=os.getenv("DEFAULT_CURRENCY", "₹")
        )
        
    except Exception as e:
        log.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/settings", summary="Update system settings")
async def update_settings(settings: SettingsUpdate):
    """
    Update system settings (runtime only, does not persist to .env)
    
    Note: This updates runtime environment variables only.
    To persist changes, edit the .env file directly.
    """
    try:
        updated = []
        
        if settings.ollama_model:
            os.environ["OLLAMA_MODEL"] = settings.ollama_model
            updated.append("ollama_model")
        
        if settings.default_country:
            os.environ["DEFAULT_COUNTRY"] = settings.default_country
            updated.append("default_country")
        
        if settings.default_currency:
            os.environ["DEFAULT_CURRENCY"] = settings.default_currency
            updated.append("default_currency")
        
        log.info(f"Updated settings: {', '.join(updated)}")
        
        return {
            "status": "success",
            "message": "Settings updated (runtime only)",
            "updated_fields": updated,
            "note": "Changes will be lost on restart. Edit .env file to persist."
        }
        
    except Exception as e:
        log.error(f"Failed to update settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
