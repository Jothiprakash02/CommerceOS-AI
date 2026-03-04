from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel


# ── Sub-module outputs ──────────────────────────────────────────────────────

class PositioningResult(BaseModel):
    positioning_type: str          # "Premium" | "Value Differentiation" | "Niche" | "Competitive Value"
    core_message: str
    price_psychology: str
    tone: str                      # e.g. "Aspirational" | "Trustworthy" | "Challenger"


class AudienceProfile(BaseModel):
    primary_audience: str
    secondary_audience: str
    age_range: str
    pain_points: List[str]
    buying_motivators: List[str]


class DifferentiationStrategy(BaseModel):
    tactics: List[str]
    bundle_suggestion: Optional[str] = None
    packaging_advice: str
    brand_building_tip: str


class ListingContent(BaseModel):
    seo_title: str
    bullet_points: List[str]       # exactly 5
    product_description: str
    cta: str
    backend_keywords: List[str]


class AdStrategy(BaseModel):
    facebook_hook: str
    instagram_concept: str
    google_ad_copy: str
    offer_strategy: str
    content_angle: str


# ── Master bundle ───────────────────────────────────────────────────────────

class StrategyBundle(BaseModel):
    positioning: PositioningResult
    audience: AudienceProfile
    differentiation: DifferentiationStrategy
    listing_content: ListingContent
    ad_strategy: AdStrategy


# ── Input ───────────────────────────────────────────────────────────────────

class StrategyInput(BaseModel):
    # From Module 1
    niche: str
    budget: float
    risk_level: str
    experience: str
    country: str
    currency_symbol: str

    # From Module 2
    demand_score: float
    competition_score: float
    trend_direction: str
    top_keywords: List[str]

    # From Module 3
    selling_price: float
    final_margin: float
    monthly_profit: float
    risk_level_m3: str             # Low | Moderate | High
    market_power_index: float
    unit_profit: float
    adjusted_volume: int
