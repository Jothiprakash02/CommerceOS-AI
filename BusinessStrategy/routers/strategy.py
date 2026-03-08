"""
Module 4 — Business Strategy Router
Endpoint: POST /strategy
"""
from fastapi import APIRouter, HTTPException
import logging

from BusinessStrategy.schemas.strategy_schema import StrategyInput
from BusinessStrategy.services.strategy_bundle import generate_business_strategy

router = APIRouter()
log = logging.getLogger(__name__)


@router.post("/strategy", summary="Generate Business Strategy (Module 4)")
async def generate_strategy(request: StrategyInput):
    """
    Generate complete business strategy including:
    - Positioning & brand tone
    - Target audience segments
    - Differentiation tactics
    - SEO-optimized listing content
    - Platform-specific ad strategy
    
    Requires: Product analysis data from Module 2
    """
    try:
        log.info(f"M4 strategy request for niche='{request.niche}'")
        
        strategy = generate_business_strategy(request)
        
        return {
            "status": "success",
            "niche": request.niche,
            "strategy": strategy.dict()
        }
        
    except Exception as e:
        log.error(f"M4 strategy generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Strategy generation failed: {str(e)}"
        )
