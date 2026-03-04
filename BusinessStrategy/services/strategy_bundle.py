"""
Strategy Bundle Orchestrator — Module 4 Main Entry Point
Chains all 5 submodules: Positioning → Audience → Differentiation → Listing → Ads
"""
from __future__ import annotations
import logging

from BusinessStrategy.schemas.strategy_schema import StrategyBundle, StrategyInput
from BusinessStrategy.services.positioning_engine    import run_positioning
from BusinessStrategy.services.audience_generator    import run_audience
from BusinessStrategy.services.differentiation_engine import run_differentiation
from BusinessStrategy.services.listing_generator     import generate_listing
from BusinessStrategy.services.ad_strategy           import run_ad_strategy

log = logging.getLogger(__name__)


def generate_business_strategy(inp: StrategyInput) -> StrategyBundle:
    """
    Full Module 4 pipeline:
      1. Positioning Engine        → brand tone & price psychology
      2. Audience Generator        → primary + secondary segments
      3. Differentiation Engine    → competitive tactics
      4. Listing Content Generator → SEO title, bullets, description (LLM)
      5. Ad Strategy Generator     → platform-specific ad hooks & offer
    """
    log.info(
        "M4 strategy for niche='%s' MPI=%.3f comp=%.1f price=%.2f",
        inp.niche, inp.market_power_index, inp.competition_score, inp.selling_price,
    )

    positioning     = run_positioning(inp)
    audience        = run_audience(inp)
    differentiation = run_differentiation(inp)
    listing         = generate_listing(inp, positioning, audience)
    ads             = run_ad_strategy(inp)

    log.info("M4 complete — positioning=%s  tone=%s", positioning.positioning_type, positioning.tone)

    return StrategyBundle(
        positioning     = positioning,
        audience        = audience,
        differentiation = differentiation,
        listing_content = listing,
        ad_strategy     = ads,
    )
