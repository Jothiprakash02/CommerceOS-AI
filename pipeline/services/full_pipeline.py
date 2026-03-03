"""
Full pipeline: Module 1 → Module 2 → Module 3
Accepts raw user input, returns unified analysis result.
"""

import sys
import os

_ROOT   = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
_GLOBAL = os.path.join(_ROOT, "global")
_M2     = os.path.join(_ROOT, "AiMarketResearch")

for _p in (_ROOT, _GLOBAL, _M2):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Module 1 — input processing
from InputConfig.services.input_processor import process_user_input
from InputConfig.utils.config_maps import COUNTRY_FEES, MARGIN_TARGET
from InputConfig.schemas.response_schema import ProcessedConfig

# Module 2 — market research (attribute-access dataclasses)
from services.data_collection   import collect_signals
from services.scoring_engine    import score_product
from services.profit_simulation import simulate_profit
from services.llm_engine        import get_llm_strategy
from services.supplier_pricing  import get_supplier_cost

# Module 3 — profit optimizer
from ProfitOptimizer.services.optimizer          import optimize_profit
from ProfitOptimizer.schemas.optimization_schema import OptimizationInput

from pipeline.schemas.pipeline_schema import PipelineResponse, MarketSummary


def run_full_pipeline(raw_input: dict) -> PipelineResponse:
    """Chain M1 → M2 → M3 and return a unified response."""

    # ── Module 1: Profile ───────────────────────────────────────────────────
    profile_dict = process_user_input(raw_input)     # returns plain dict
    profile      = ProcessedConfig(**profile_dict)

    product     = profile.niche
    country     = profile.country
    budget      = profile.budget
    platform    = profile.platform
    base_margin = profile.target_margin
    country_fee = profile.country_fee

    # ── Module 2: Market signals ────────────────────────────────────────────
    signals = collect_signals(product, country)      # CollectedSignals dataclass
    scores  = score_product(signals)                  # ScoringResult dataclass

    demand_score      = float(scores.demand_score)
    competition_score = float(scores.competition_score)
    viability_score   = float(scores.viability_score)
    confidence_score  = float(scores.confidence_score)
    margin_pct        = float(scores.margin_pct)
    risk_level_m2     = scores.risk_level
    viability_label   = scores.viability_label

    # Use avg_price from Amazon as market reference price
    avg_market_price = float(signals.avg_price) if signals.avg_price else 0.0

    # Supplier cost → use landed cost (local currency)
    supplier_data = get_supplier_cost(product, country, retail_price=avg_market_price or None)
    cost_per_unit = float(supplier_data.get("landed_cost_local") or
                          supplier_data.get("fob_price_usd") or 1.0)
    if cost_per_unit <= 0:
        cost_per_unit = 1.0

    # Preliminary simulation (price=0 is invalid; use avg_market_price or 1 as placeholder)
    sim_price = max(avg_market_price, cost_per_unit * 1.5, 1.0)
    sim = simulate_profit(
        demand_score  = demand_score,
        price         = sim_price,
        cost_per_unit = cost_per_unit,
        budget        = budget,
        bsr           = signals.bsr,
    )
    estimated_sales = int(sim.estimated_monthly_sales)

    # Trend direction derived from trend_growth (no direct field in CollectedSignals)
    trend_direction = (
        "rising"  if signals.trend_growth > 10 else
        "falling" if signals.trend_growth < -10 else
        "stable"
    )

    # Keywords: use product niche as primary keyword (keyword_research returns metrics, not lists)
    top_keywords = [product] + [
        f"{product} {suffix}"
        for suffix in ("buy online", "best price", "review", "vs")
    ][:4]

    # LLM strategy — keyword-only function with many required params
    try:
        llm_result = get_llm_strategy(
            product                  = product,
            country                  = country,
            platform                 = platform,
            demand_score             = demand_score,
            competition_score        = competition_score,
            viability_score          = viability_score,
            risk_level               = risk_level_m2,
            viability_label          = viability_label,
            margin_pct               = margin_pct,
            avg_market_price         = avg_market_price,
            suggested_price          = sim_price,
            estimated_monthly_profit = float(sim.estimated_monthly_profit),
            roi_percent              = float(sim.roi_percent),
            break_even_months        = float(sim.break_even_months),
            budget                   = budget,
            confidence_score         = confidence_score,
        )
        # LLMStrategy dataclass: positioning_strategy + final_recommendation
        strategy_text = (
            f"{llm_result.positioning_strategy}\n\n"
            f"Recommendation: {llm_result.final_recommendation}\n\n"
            f"Market Entry: {llm_result.market_entry_advice}"
        )
    except Exception as exc:
        strategy_text = f"LLM strategy unavailable ({exc})."

    market = MarketSummary(
        demand_score      = demand_score,
        competition_score = competition_score,
        trend_direction   = trend_direction,
        top_keywords      = top_keywords,
        supplier_cost     = cost_per_unit,
        estimated_sales   = estimated_sales,
        llm_strategy      = strategy_text,
    )

    # ── Module 3: Profit optimization ──────────────────────────────────────
    opt_input = OptimizationInput(
        budget            = budget,
        base_margin       = base_margin,
        country_fee       = country_fee,
        estimated_sales   = estimated_sales,
        demand_score      = demand_score,
        competition_score = competition_score,
        cost_per_unit     = cost_per_unit,
    )
    optimization = optimize_profit(opt_input)

    return PipelineResponse(
        status       = "success",
        profile      = profile,
        market       = market,
        optimization = optimization,
        message      = (
            f"Full analysis complete for '{product}' in {country}. "
            f"Risk: {optimization.risk_level}. "
            f"Recommended price: ${optimization.selling_price:.2f}."
        ),
    )
