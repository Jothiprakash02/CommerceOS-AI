"""
Opportunity Ranking Engine
===========================
Implements directive formula:

Opportunity Score = 0.40 × demand
                  + 0.30 × competition_gap  
                  + 0.20 × profitability
                  + 0.10 × trend_stability

Higher score = better opportunity
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

log = logging.getLogger(__name__)


@dataclass
class RankedOpportunity:
    """Ranked product opportunity"""
    product_name: str
    opportunity_score: float  # 0-100
    rank: int
    
    # Component scores
    demand_score: float
    competition_gap_score: float
    profitability_score: float
    trend_stability_score: float
    
    # Supporting data
    trend_strength: float
    search_volume: int
    estimated_margin: float
    confidence: float
    
    # Recommendation
    recommendation: str


def calculate_competition_gap(
    seller_count: int,
    avg_reviews: float,
    sponsored_density: float
) -> float:
    """
    Competition gap (0-100)
    Higher = less competition = better opportunity
    
    This is inverse of competition intensity
    """
    # Low seller count = high gap
    seller_gap = max(0, 100 - (seller_count * 2))  # 50+ sellers = 0 gap
    
    # Low reviews = high gap (easier to compete)
    review_gap = max(0, 100 - (avg_reviews / 50))  # 5000+ reviews = 0 gap
    
    # Low ad density = high gap
    ad_gap = (1 - sponsored_density) * 100
    
    # Weighted average
    gap = (0.40 * seller_gap + 0.35 * review_gap + 0.25 * ad_gap)
    
    return min(gap, 100.0)


def calculate_profitability_score(
    avg_price: float,
    estimated_cost: float,
    platform_fee_pct: float = 15.0
) -> float:
    """
    Profitability score (0-100)
    Based on estimated profit margin
    """
    if avg_price == 0 or estimated_cost == 0:
        return 50.0  # Neutral if no data
    
    # Calculate estimated margin
    revenue = avg_price
    cost = estimated_cost
    platform_fee = revenue * (platform_fee_pct / 100)
    ad_cost = revenue * 0.10  # Assume 10% ad spend
    
    profit = revenue - cost - platform_fee - ad_cost
    margin_pct = (profit / revenue) * 100 if revenue > 0 else 0
    
    # Score based on margin
    if margin_pct >= 40:
        score = 100.0
    elif margin_pct >= 30:
        score = 85.0
    elif margin_pct >= 20:
        score = 65.0
    elif margin_pct >= 10:
        score = 40.0
    else:
        score = 20.0
    
    return score


def calculate_trend_stability_score(
    trend_growth: float,
    trend_avg: float,
    seasonality_variance: float
) -> float:
    """
    Trend stability (0-100)
    Higher = more stable = better
    """
    # Moderate positive growth is most stable
    if 10 <= trend_growth <= 30:
        growth_stability = 100.0
    elif 0 <= trend_growth < 10:
        growth_stability = 80.0
    elif 30 < trend_growth <= 50:
        growth_stability = 70.0
    elif trend_growth > 50:  # Too fast = bubble risk
        growth_stability = 40.0
    else:  # Negative growth
        growth_stability = 20.0
    
    # High average = stable demand
    if trend_avg >= 70:
        avg_stability = 100.0
    elif trend_avg >= 50:
        avg_stability = 80.0
    elif trend_avg >= 30:
        avg_stability = 60.0
    else:
        avg_stability = 30.0
    
    # Low seasonality = stable
    seasonal_stability = max(0, 100 - (seasonality_variance * 4))
    
    # Weighted average
    stability = (
        0.40 * growth_stability +
        0.35 * avg_stability +
        0.25 * seasonal_stability
    )
    
    return min(stability, 100.0)


def rank_opportunities(
    opportunities: List[dict],
    platform: str = "Amazon",
    country: str = "India"
) -> List[RankedOpportunity]:
    """
    Rank opportunities using directive formula
    
    Input format:
    {
        "product_name": str,
        "trend_strength": float,
        "trend_growth": float,
        "trend_avg": float,
        "seasonality_variance": float,
        "search_volume": int,
        "avg_price": float,
        "estimated_cost": float,
        "seller_count": int,
        "avg_reviews": float,
        "sponsored_density": float,
        "confidence": float
    }
    """
    
    ranked = []
    
    for opp in opportunities:
        # Calculate component scores
        demand_score = min(
            (opp.get("trend_strength", 50) * 0.5) +
            (opp.get("search_volume", 0) / 1000 * 0.5),  # Normalize search volume
            100.0
        )
        
        competition_gap_score = calculate_competition_gap(
            opp.get("seller_count", 20),
            opp.get("avg_reviews", 500),
            opp.get("sponsored_density", 0.3)
        )
        
        profitability_score = calculate_profitability_score(
            opp.get("avg_price", 0),
            opp.get("estimated_cost", 0)
        )
        
        trend_stability_score = calculate_trend_stability_score(
            opp.get("trend_growth", 0),
            opp.get("trend_avg", 50),
            opp.get("seasonality_variance", 10)
        )
        
        # Apply directive formula
        opportunity_score = (
            0.40 * demand_score +
            0.30 * competition_gap_score +
            0.20 * profitability_score +
            0.10 * trend_stability_score
        )
        
        # Generate recommendation
        if opportunity_score >= 75:
            recommendation = "Excellent opportunity. High priority for launch."
        elif opportunity_score >= 60:
            recommendation = "Strong opportunity. Recommended for consideration."
        elif opportunity_score >= 45:
            recommendation = "Moderate opportunity. Requires careful analysis."
        else:
            recommendation = "Weak opportunity. Consider alternatives."
        
        # Calculate estimated margin for display
        if opp.get("avg_price", 0) > 0 and opp.get("estimated_cost", 0) > 0:
            revenue = opp["avg_price"]
            cost = opp["estimated_cost"]
            platform_fee = revenue * 0.15
            ad_cost = revenue * 0.10
            profit = revenue - cost - platform_fee - ad_cost
            estimated_margin = (profit / revenue) * 100 if revenue > 0 else 0
        else:
            estimated_margin = 0
        
        ranked.append(RankedOpportunity(
            product_name=opp.get("product_name", "Unknown"),
            opportunity_score=round(opportunity_score, 2),
            rank=0,  # Will be set after sorting
            demand_score=round(demand_score, 2),
            competition_gap_score=round(competition_gap_score, 2),
            profitability_score=round(profitability_score, 2),
            trend_stability_score=round(trend_stability_score, 2),
            trend_strength=opp.get("trend_strength", 0),
            search_volume=opp.get("search_volume", 0),
            estimated_margin=round(estimated_margin, 2),
            confidence=opp.get("confidence", 0),
            recommendation=recommendation
        ))
    
    # Sort by opportunity score (descending)
    ranked.sort(key=lambda x: x.opportunity_score, reverse=True)
    
    # Assign ranks
    for i, opp in enumerate(ranked, 1):
        opp.rank = i
    
    log.info(f"Ranked {len(ranked)} opportunities using directive formula")
    
    return ranked
