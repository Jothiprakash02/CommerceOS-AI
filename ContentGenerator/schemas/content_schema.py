"""
Content Generation Request/Response Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from enum import Enum


class Platform(str, Enum):
    """Supported platforms"""
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    PINTEREST = "pinterest"
    AMAZON = "amazon"
    ETSY = "etsy"
    SHOPIFY = "shopify"


class ContentType(str, Enum):
    """Types of content to generate"""
    PRODUCT_DESCRIPTION = "product_description"
    SOCIAL_POST = "social_post"
    HASHTAGS = "hashtags"
    META_DESCRIPTION = "meta_description"
    AD_COPY = "ad_copy"
    BULLET_POINTS = "bullet_points"
    ALL = "all"


class Tone(str, Enum):
    """Content tone"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    ENTHUSIASTIC = "enthusiastic"
    LUXURY = "luxury"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"


class Length(str, Enum):
    """Content length"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class ContentRequest(BaseModel):
    """Request for content generation"""
    
    # Input (flexible)
    product_name: Optional[str] = Field(None, description="Product name")
    product_description: Optional[str] = Field(None, description="Product description")
    product_category: Optional[str] = Field(None, description="Product category")
    target_audience: Optional[str] = Field(None, description="Target audience")
    key_features: Optional[List[str]] = Field(None, description="Key product features")
    keywords: Optional[List[str]] = Field(None, description="SEO keywords to include")
    
    # From analysis (if available)
    analysis_data: Optional[Dict] = Field(None, description="Product analysis data")
    
    # Generation options
    platforms: List[Platform] = Field(
        default=[Platform.INSTAGRAM, Platform.TWITTER, Platform.FACEBOOK],
        description="Platforms to generate content for"
    )
    content_types: List[ContentType] = Field(
        default=[ContentType.ALL],
        description="Types of content to generate"
    )
    tone: Tone = Field(default=Tone.PROFESSIONAL, description="Content tone")
    length: Length = Field(default=Length.MEDIUM, description="Content length")
    variations: int = Field(default=3, ge=1, le=5, description="Number of variations")
    
    # Additional options
    include_emojis: bool = Field(default=True, description="Include emojis in social posts")
    include_call_to_action: bool = Field(default=True, description="Include CTA")
    focus_seo: bool = Field(default=True, description="Optimize for SEO")


class PlatformContent(BaseModel):
    """Content for a specific platform"""
    platform: Platform
    
    # Social media content
    post: Optional[str] = None
    hashtags: Optional[List[str]] = None
    character_count: Optional[int] = None
    
    # E-commerce content
    title: Optional[str] = None
    description: Optional[str] = None
    bullet_points: Optional[List[str]] = None
    meta_description: Optional[str] = None
    
    # Ad copy
    ad_headline: Optional[str] = None
    ad_body: Optional[str] = None
    call_to_action: Optional[str] = None
    
    # SEO
    seo_keywords: Optional[List[str]] = None
    seo_score: Optional[int] = None


class ContentVariation(BaseModel):
    """A variation of generated content"""
    variation_number: int
    platforms: List[PlatformContent]


class ContentResponse(BaseModel):
    """Response with generated content"""
    
    # Input summary
    product_name: str
    generated_for: List[Platform]
    tone: Tone
    length: Length
    
    # Generated content
    variations: List[ContentVariation]
    
    # Universal content (works everywhere)
    universal_description: str
    universal_hashtags: List[str]
    seo_keywords: List[str]
    
    # Metadata
    generation_time: float
    model_used: str
    success: bool = True
    message: Optional[str] = None


class QuickGenerateRequest(BaseModel):
    """Quick generation with minimal input"""
    product_name: str = Field(..., description="Product name")
    platform: Platform = Field(default=Platform.INSTAGRAM, description="Target platform")
    tone: Tone = Field(default=Tone.CASUAL, description="Content tone")
