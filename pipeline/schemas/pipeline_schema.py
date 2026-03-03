from pydantic import BaseModel
from typing import Optional, Dict, Any
from InputConfig.schemas.response_schema import ProcessedConfig
from ProfitOptimizer.schemas.optimization_schema import OptimizationResult


class PipelineRequest(BaseModel):
    niche: str
    budget: float
    risk_level: str          # conservative | moderate | aggressive
    country: str             # US | UK | IN | DE | CA | AU
    experience: str          # beginner | intermediate | expert


class MarketSummary(BaseModel):
    demand_score: float
    competition_score: float
    trend_direction: str
    top_keywords: list
    supplier_cost: float
    estimated_sales: int
    llm_strategy: Optional[str] = None


class PipelineResponse(BaseModel):
    status: str
    profile: ProcessedConfig
    market: MarketSummary
    optimization: OptimizationResult
    message: str
