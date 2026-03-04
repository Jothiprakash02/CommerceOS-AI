"""
Positioning Engine — Module 4 Submodule 1
Determines optimal brand/price positioning from MPI, margin, and competition.
"""
from BusinessStrategy.schemas.strategy_schema import PositioningResult, StrategyInput


def run_positioning(inp: StrategyInput) -> PositioningResult:
    mpi   = inp.market_power_index
    margin = inp.final_margin
    comp  = inp.competition_score
    dem   = inp.demand_score
    sym   = inp.currency_symbol
    price = inp.selling_price

    # Charm price: one below nearest round hundred/ten
    def charm(p: float) -> str:
        import math
        if p >= 100:
            rounded = math.ceil(p / 100) * 100
            charm_p = rounded - 1
        elif p >= 10:
            rounded = math.ceil(p / 10) * 10
            charm_p = rounded - 1
        else:
            charm_p = p
        return f"{sym}{charm_p:.0f} instead of {sym}{math.ceil(p / 10) * 10:.0f}"

    # ── Decision tree ───────────────────────────────────────────────────────
    if mpi > 0.7 and margin > 0.30:
        ptype = "Premium"
        core  = (f"Position as the top-tier choice in {inp.niche}. "
                 "Emphasize quality, reliability, and brand trust over price.")
        tone  = "Aspirational"

    elif dem > 60 and comp > 60:
        ptype = "Value Differentiation"
        core  = (f"Compete head-on in a crowded {inp.niche} market by offering "
                 "the best value-to-price ratio. Lead with social proof and reviews.")
        tone  = "Challenger"

    elif mpi < 0.5:
        ptype = "Niche Targeting"
        core  = (f"Target an underserved sub-segment within {inp.niche}. "
                 "Build community and authority before scaling ad spend.")
        tone  = "Trustworthy"

    elif comp < 40:
        ptype = "Market Pioneer"
        core  = (f"Be the first mover in a low-competition {inp.niche} space. "
                 "Invest in brand awareness and category education.")
        tone  = "Educational"

    else:
        ptype = "Competitive Value"
        core  = (f"Offer solid value in {inp.niche} while differentiating on "
                 "secondary attributes: design, packaging, or after-sales support.")
        tone  = "Friendly"

    risk_map = {
        "conservative": "anchor pricing close to market average",
        "moderate":     "competitive mid-range pricing",
        "aggressive":   "slightly below market to drive initial volume",
    }
    psych_hint = risk_map.get(inp.risk_level, "competitive mid-range pricing")

    return PositioningResult(
        positioning_type = ptype,
        core_message     = core,
        price_psychology = f"{charm(price)} — {psych_hint}",
        tone             = tone,
    )
