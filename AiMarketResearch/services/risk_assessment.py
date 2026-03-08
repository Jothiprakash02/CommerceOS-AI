"""
Enhanced Risk Assessment Engine
================================
Implements the directive's risk formula:

Risk Score = 0.35 × competition_intensity
           + 0.30 × demand_volatility  
           + 0.20 × margin_risk
           + 0.15 × trend_instability

Lower risk score = better opportunity
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Tuple

log = logging.getLogger(__name__)


@dataclass
class RiskAssessment:
    """Enhanced risk assessment result"""
    risk_score: float  # 0-100, lower is better
    risk_level: str    # Low / Medium / High
    recommendation: str
    
    # Component scores
    competition_intensity: float
    demand_volatility: float
    margin_risk: float
    trend_instability: float
    
    # Decision support
    should_launch: bool
    confidence: float


def calculate_competition_intensity(
    competition_score: float,
    seller_count: int,
    sponsored_density: float
) -> float:
    """
    Competition intensity (0-100)
    Higher = more intense competition
    """
    # Base from competition score
    base = competition_score
    
    # Adjust for seller count (>50 sellers = very competitive)
    seller_factor = min(seller_count / 50, 1.0) * 20
    
    # Adjust for sponsored ads (>0.5 density = high ad spend)
    ad_factor = sponsored_density * 30
    
    intensity = base + seller_factor + ad_factor
    return min(intensity, 100.0)


def calculate_demand_volatility(
    trend_growth: float,
    seasonality_variance: float,
    trend_avg: float
) -> float:
    """
    Demand volatility (0-100)
    Higher = more volatile/unstable demand
    """
    # High growth can indicate volatility
    growth_volatility = abs(trend_growth) / 2  # -100 to +100 → 0 to 50
    
    # Seasonality variance indicates instability
    seasonal_volatility = seasonality_variance * 2  # 0-25 → 0-50
    
    # Low average trend = uncertain demand
    low_demand_penalty = max(0, (50 - trend_avg) / 2)  # 0-25
    
    volatility = growth_volatility + seasonal_volatility + low_demand_penalty
    return min(volatility, 100.0)


def calculate_margin_risk(
    profit_margin: float,
    cost_per_unit: float,
    selling_price: float
) -> float:
    """
    Margin risk (0-100)
    Higher = riskier margins
    """
    # Low margin = high risk
    if profit_margin < 15:
        margin_risk = 80.0
    elif profit_margin < 25:
        margin_risk = 50.0
    elif profit_margin < 35:
        margin_risk = 30.0
    else:
        margin_risk = 10.0
    
    # Very low price point = risky
    if selling_price < 500:  # Less than ₹500
        margin_risk += 20
    
    # High cost = risky
    if cost_per_unit > selling_price * 0.7:  # Cost > 70% of price
        margin_risk += 15
    
    return min(margin_risk, 100.0)


def calculate_trend_instability(
    trend_growth: float,
    trend_avg: float,
    seasonality_variance: float
) -> float:
    """
    Trend instability (0-100)
    Higher = more unstable trend
    """
    # Negative growth = unstable
    if trend_growth < -20:
        instability = 80.0
    elif trend_growth < 0:
        instability = 50.0
    elif trend_growth > 50:  # Too fast growth can be bubble
        instability = 40.0
    else:
        instability = 20.0
    
    # Low average = unstable
    if trend_avg < 30:
        instability += 30
    elif trend_avg < 50:
        instability += 15
    
    # High seasonality = unstable
    instability += seasonality_variance * 2
    
    return min(instability, 100.0)


def assess_risk(
    # Scores
    demand_score: float,
    competition_score: float,
    profit_margin: float,
    
    # Raw signals
    trend_growth: float,
    trend_avg: float,
    seasonality_variance: float,
    seller_count: int,
    sponsored_density: float,
    cost_per_unit: float,
    selling_price: float,
    
    # Confidence
    data_confidence: float
) -> RiskAssessment:
    """
    Calculate comprehensive risk assessment using directive formula
    """
    
    # Calculate component scores
    competition_intensity = calculate_competition_intensity(
        competition_score, seller_count, sponsored_density
    )
    
    demand_volatility = calculate_demand_volatility(
        trend_growth, seasonality_variance, trend_avg
    )
    
    margin_risk = calculate_margin_risk(
        profit_margin, cost_per_unit, selling_price
    )
    
    trend_instability = calculate_trend_instability(
        trend_growth, trend_avg, seasonality_variance
    )
    
    # Apply directive formula
    risk_score = (
        0.35 * competition_intensity +
        0.30 * demand_volatility +
        0.20 * margin_risk +
        0.15 * trend_instability
    )
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "Low"
        recommendation = "Strong opportunity. Proceed with launch."
        should_launch = True
    elif risk_score < 50:
        risk_level = "Medium"
        recommendation = "Moderate risk. Launch with controlled budget and monitor closely."
        should_launch = True
    elif risk_score < 70:
        risk_level = "High"
        recommendation = "High risk. Consider alternative products or test with minimal investment."
        should_launch = False
    else:
        risk_level = "Very High"
        recommendation = "Very high risk. Not recommended for launch. Explore other opportunities."
        should_launch = False
    
    log.info(
        f"Risk Assessment: score={risk_score:.1f} level={risk_level} "
        f"(comp={competition_intensity:.1f} vol={demand_volatility:.1f} "
        f"margin={margin_risk:.1f} trend={trend_instability:.1f})"
    )
    
    return RiskAssessment(
        risk_score=round(risk_score, 2),
        risk_level=risk_level,
        recommendation=recommendation,
        competition_intensity=round(competition_intensity, 2),
        demand_volatility=round(demand_volatility, 2),
        margin_risk=round(margin_risk, 2),
        trend_instability=round(trend_instability, 2),
        should_launch=should_launch,
        confidence=data_confidence
    )
