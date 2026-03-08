"""
Launch Strategy Generator
==========================
Generates structured week-by-week launch plan based on:
- Risk level
- Budget
- Competition intensity
- Product type
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

log = logging.getLogger(__name__)


@dataclass
class WeeklyTask:
    """Single task in launch timeline"""
    week: int
    title: str
    description: str
    priority: str  # High / Medium / Low
    estimated_cost: float
    success_metric: str


@dataclass
class LaunchStrategy:
    """Complete launch strategy"""
    timeline_weeks: int
    total_estimated_cost: float
    weekly_tasks: List[WeeklyTask]
    critical_success_factors: List[str]
    risk_mitigation_steps: List[str]
    recommended_budget_allocation: dict


def generate_launch_strategy(
    product_name: str,
    risk_level: str,
    budget: float,
    competition_score: float,
    demand_score: float,
    selling_price: float,
    platform: str = "Amazon"
) -> LaunchStrategy:
    """
    Generate structured launch plan
    """
    
    # Determine timeline based on risk
    if risk_level == "Low":
        timeline_weeks = 4
    elif risk_level == "Medium":
        timeline_weeks = 6
    else:  # High
        timeline_weeks = 8
    
    # Build weekly tasks
    tasks = []
    
    # Week 1: Validation
    tasks.append(WeeklyTask(
        week=1,
        title="Demand Validation",
        description="Create landing page and run micro-ads to validate demand. Collect email signups.",
        priority="High",
        estimated_cost=budget * 0.05,  # 5% of budget
        success_metric="50+ email signups or 2% conversion rate"
    ))
    
    # Week 2: Development/Sourcing
    if competition_score > 60:
        # High competition - need differentiation
        tasks.append(WeeklyTask(
            week=2,
            title="Develop Differentiated MVP",
            description="Build MVP with unique features identified in competitor analysis. Focus on gaps in market.",
            priority="High",
            estimated_cost=budget * 0.30,  # 30% of budget
            success_metric="MVP ready with 2-3 unique features"
        ))
    else:
        # Lower competition - faster to market
        tasks.append(WeeklyTask(
            week=2,
            title="Source/Develop Product",
            description="Finalize product sourcing or development. Ensure quality meets market standards.",
            priority="High",
            estimated_cost=budget * 0.25,  # 25% of budget
            success_metric="Product ready for launch"
        ))
    
    # Week 3: Listing Optimization
    tasks.append(WeeklyTask(
        week=3,
        title="Create Optimized Listing",
        description=f"Launch on {platform} with SEO-optimized title, images, and description. Use AI-generated content.",
        priority="High",
        estimated_cost=budget * 0.10,  # 10% for photography/design
        success_metric="Listing live with 5+ high-quality images"
    ))
    
    # Week 4: Initial Marketing
    if demand_score > 70:
        # High demand - aggressive marketing
        tasks.append(WeeklyTask(
            week=4,
            title="Launch Marketing Campaign",
            description="Run PPC ads at 15% of revenue target. Focus on high-intent keywords.",
            priority="High",
            estimated_cost=budget * 0.25,  # 25% for ads
            success_metric="10+ sales in first week"
        ))
    else:
        # Lower demand - conservative marketing
        tasks.append(WeeklyTask(
            week=4,
            title="Soft Launch with Targeted Ads",
            description="Run conservative PPC campaign at 10% of revenue. Test different ad copy.",
            priority="Medium",
            estimated_cost=budget * 0.15,  # 15% for ads
            success_metric="5+ sales in first week"
        ))
    
    # Additional weeks for higher risk
    if timeline_weeks >= 6:
        tasks.append(WeeklyTask(
            week=5,
            title="Gather Initial Reviews",
            description="Follow up with customers for reviews. Offer excellent support to ensure 5-star ratings.",
            priority="High",
            estimated_cost=budget * 0.05,  # 5% for review incentives
            success_metric="10+ verified reviews with 4.5+ average"
        ))
        
        tasks.append(WeeklyTask(
            week=6,
            title="Optimize Based on Data",
            description="Analyze sales data, adjust pricing if needed, optimize ad spend, improve listing based on customer feedback.",
            priority="Medium",
            estimated_cost=budget * 0.10,  # 10% for optimization
            success_metric="20% improvement in conversion rate"
        ))
    
    if timeline_weeks >= 8:
        tasks.append(WeeklyTask(
            week=7,
            title="Scale Marketing",
            description="Increase ad budget by 50% if ROI is positive. Expand to additional keywords.",
            priority="Medium",
            estimated_cost=budget * 0.15,  # 15% for scaling
            success_metric="2x sales from week 4"
        ))
        
        tasks.append(WeeklyTask(
            week=8,
            title="Evaluate and Pivot",
            description="Comprehensive review of all metrics. Decide: scale, optimize, or pivot to new product.",
            priority="High",
            estimated_cost=0,
            success_metric="Clear decision on next steps"
        ))
    
    # Calculate total cost
    total_cost = sum(task.estimated_cost for task in tasks)
    
    # Critical success factors
    success_factors = [
        f"Achieve {selling_price * 15:.0f}₹ in sales by week 4",
        "Maintain 4.5+ star rating",
        "Keep customer acquisition cost below 30% of selling price",
        "Respond to all customer inquiries within 24 hours"
    ]
    
    if competition_score > 60:
        success_factors.append("Clearly communicate unique value proposition in all marketing")
    
    if demand_score < 50:
        success_factors.append("Focus on niche targeting rather than broad marketing")
    
    # Risk mitigation
    mitigation_steps = []
    
    if risk_level in ["High", "Very High"]:
        mitigation_steps.extend([
            "Start with minimum viable inventory (10-20 units)",
            "Test pricing with A/B testing before committing to large inventory",
            "Set strict budget limits for marketing spend"
        ])
    
    if competition_score > 70:
        mitigation_steps.extend([
            "Focus on underserved customer segments",
            "Emphasize unique features in all communications",
            "Consider bundling or value-added services"
        ])
    
    if demand_score < 40:
        mitigation_steps.extend([
            "Validate demand with pre-orders before full launch",
            "Build email list before product launch",
            "Consider alternative channels beyond primary platform"
        ])
    
    # Budget allocation
    budget_allocation = {
        "product_development": 30,
        "marketing": 35,
        "listing_optimization": 10,
        "customer_acquisition": 15,
        "contingency": 10
    }
    
    log.info(
        f"Generated {timeline_weeks}-week launch strategy for '{product_name}' "
        f"with {len(tasks)} tasks and ₹{total_cost:.0f} estimated cost"
    )
    
    return LaunchStrategy(
        timeline_weeks=timeline_weeks,
        total_estimated_cost=round(total_cost, 2),
        weekly_tasks=tasks,
        critical_success_factors=success_factors,
        risk_mitigation_steps=mitigation_steps,
        recommended_budget_allocation=budget_allocation
    )
