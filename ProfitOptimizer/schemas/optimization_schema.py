from pydantic import BaseModel
from typing import Literal


class OptimizationInput(BaseModel):
    # From Module 1 (processed config)
    budget: float
    base_margin: float          # from MARGIN_TARGET map
    country_fee: float          # from COUNTRY_FEES map
    estimated_sales: int        # from Module 2 simulated_monthly_sales

    # From Module 2 scores
    demand_score: float         # 0-100
    competition_score: float    # 0-100

    # From Module 2 supplier pricing
    cost_per_unit: float


class OptimizationResult(BaseModel):
    market_power_index: float
    final_margin: float
    selling_price: float
    unit_profit: float
    adjusted_volume: int
    monthly_profit: float
    recommended_inventory: int
    risk_level: Literal["Low", "Moderate", "High"]
