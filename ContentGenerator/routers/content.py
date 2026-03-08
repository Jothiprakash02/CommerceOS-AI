"""
Content Generation API Router
"""

import logging
import sys
import os

# Path setup
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for _p in [_ROOT, os.path.join(_ROOT, "global")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from fastapi import APIRouter, HTTPException
from ContentGenerator.schemas.content_schema import (
    ContentRequest,
    ContentResponse,
    QuickGenerateRequest,
    Platform,
    ContentType,
    Tone,
    Length
)
from ContentGenerator.services.content_generator import ContentGeneratorService

log = logging.getLogger(__name__)

router = APIRouter()

# Singleton service instance
_generator_service = None


def get_generator() -> ContentGeneratorService:
    """Get or create generator service instance"""
    global _generator_service
    if _generator_service is None:
        _generator_service = ContentGeneratorService()
    return _generator_service


@router.post("/generate-content", response_model=ContentResponse)
async def generate_content(request: ContentRequest):
    """
    Generate SEO-optimized content for multiple platforms.
    
    Supports:
    - Social media: Instagram, Twitter, Facebook, LinkedIn, TikTok, Pinterest
    - E-commerce: Amazon, Etsy, Shopify
    
    Content types:
    - Product descriptions
    - Social media posts
    - Hashtags
    - Meta descriptions
    - Ad copy
    - Bullet points
    """
    try:
        log.info(f"Content generation request for: {request.product_name}")
        
        generator = get_generator()
        
        # Convert enums to strings
        platforms = [p.value for p in request.platforms]
        
        # Generate content
        result = generator.generate_content(
            product_name=request.product_name,
            product_description=request.product_description,
            product_category=request.product_category,
            target_audience=request.target_audience,
            key_features=request.key_features,
            keywords=request.keywords,
            platforms=platforms,
            tone=request.tone.value,
            length=request.length.value,
            variations=request.variations,
            include_emojis=request.include_emojis,
            include_cta=request.include_call_to_action,
            focus_seo=request.focus_seo
        )
        
        return ContentResponse(**result)
        
    except Exception as exc:
        log.error(f"Content generation failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(exc)}"
        )


@router.post("/quick-generate")
async def quick_generate(request: QuickGenerateRequest):
    """
    Quick content generation with minimal input.
    Perfect for testing or simple use cases.
    """
    try:
        log.info(f"Quick generation for: {request.product_name}")
        
        generator = get_generator()
        
        result = generator.quick_generate(
            product_name=request.product_name,
            platform=request.platform.value,
            tone=request.tone.value
        )
        
        return result
        
    except Exception as exc:
        log.error(f"Quick generation failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Quick generation failed: {str(exc)}"
        )


@router.get("/platforms")
async def get_platforms():
    """Get list of supported platforms with specifications"""
    return {
        "social_media": [
            {
                "platform": "instagram",
                "name": "Instagram",
                "max_chars": 2200,
                "hashtags": "20-30",
                "style": "Visual, engaging, emoji-friendly"
            },
            {
                "platform": "twitter",
                "name": "Twitter/X",
                "max_chars": 280,
                "hashtags": "1-3",
                "style": "Concise, witty, trending"
            },
            {
                "platform": "facebook",
                "name": "Facebook",
                "max_chars": 63206,
                "hashtags": "3-5",
                "style": "Conversational, community-focused"
            },
            {
                "platform": "linkedin",
                "name": "LinkedIn",
                "max_chars": 3000,
                "hashtags": "3-5",
                "style": "Professional, value-driven"
            },
            {
                "platform": "tiktok",
                "name": "TikTok",
                "max_chars": 2200,
                "hashtags": "5-8",
                "style": "Trendy, fun, viral-worthy"
            },
            {
                "platform": "pinterest",
                "name": "Pinterest",
                "max_chars": 500,
                "hashtags": "5-10",
                "style": "Inspirational, descriptive"
            }
        ],
        "ecommerce": [
            {
                "platform": "amazon",
                "name": "Amazon",
                "title_max": 200,
                "bullet_points": 5,
                "description_max": 2000,
                "style": "Informative, keyword-rich"
            },
            {
                "platform": "etsy",
                "name": "Etsy",
                "title_max": 140,
                "tags": 13,
                "description_max": 5000,
                "style": "Artisanal, story-driven"
            },
            {
                "platform": "shopify",
                "name": "Shopify",
                "title_max": 255,
                "description_max": 65535,
                "style": "Brand-focused, conversion-optimized"
            }
        ]
    }


@router.get("/tones")
async def get_tones():
    """Get available content tones"""
    return {
        "tones": [
            {"value": "professional", "label": "Professional", "description": "Formal, authoritative, business-focused"},
            {"value": "casual", "label": "Casual", "description": "Friendly, conversational, approachable"},
            {"value": "enthusiastic", "label": "Enthusiastic", "description": "Energetic, exciting, passionate"},
            {"value": "luxury", "label": "Luxury", "description": "Premium, exclusive, sophisticated"},
            {"value": "friendly", "label": "Friendly", "description": "Warm, welcoming, personable"},
            {"value": "authoritative", "label": "Authoritative", "description": "Expert, confident, trustworthy"}
        ]
    }


@router.get("/health")
async def content_health():
    """Check if content generator is ready"""
    try:
        generator = get_generator()
        return {
            "status": "ready",
            "model": generator.model,
            "ollama_url": generator.ollama_url,
            "message": "Content generator is ready"
        }
    except Exception as exc:
        return {
            "status": "error",
            "message": str(exc)
        }
