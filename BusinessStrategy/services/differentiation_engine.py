"""
Differentiation Strategy Engine — Module 4 Submodule 3
Generates competitive tactics based on competition level and budget.
"""
from BusinessStrategy.schemas.strategy_schema import DifferentiationStrategy, StrategyInput


def run_differentiation(inp: StrategyInput) -> DifferentiationStrategy:
    comp    = inp.competition_score
    budget  = inp.budget
    niche   = inp.niche
    margin  = inp.final_margin
    exp     = inp.experience

    tactics: list[str] = []
    bundle  = None
    pack    = ""
    brand   = ""

    # ── High competition (> 70) ─────────────────────────────────────────────
    if comp > 70:
        tactics += [
            f"Bundle {niche} with complementary accessories to increase perceived value",
            "Introduce a limited-edition color or design variant to create scarcity",
            "Offer a 30-day no-questions-asked return policy to lower purchase risk",
            "Collect 20+ authentic reviews within first 2 weeks via follow-up emails",
        ]
        bundle = (f"Bundle {niche} with a carrying case, cleaning kit, or user guide "
                  "— increases AOV by 15-25% without significant cost increase")
        pack  = "Minimalist premium unboxing experience — matte finish box, branded tissue paper, thank-you card"
        brand = "Start micro-influencer seeding (1K-50K followers) for authentic social proof"

    # ── Moderate competition (40-70) ────────────────────────────────────────
    elif comp >= 40:
        tactics += [
            "Differentiate on product story: who made it, why, and what problem it solves",
            "Offer free extended warranty or lifetime support as key USP",
            f"Use keyword gap analysis — target long-tail {niche} keywords competitors miss",
            "A/B test two main image styles: lifestyle vs white-background product shot",
        ]
        bundle = None
        pack  = "Clean, professional packaging with QR code linking to usage tutorial"
        brand = f"Build a social community around {niche} usage — Instagram or YouTube shorts"

    # ── Low competition (< 40) ──────────────────────────────────────────────
    else:
        tactics += [
            "Be first to own the category narrative — publish comparison content",
            "Invest in premium brand identity: logo, photography, brand story",
            f"Own the SEO for top {niche} keywords before competition scales",
            "Offer a 'founding customer' discount to build loyal early adopters",
        ]
        pack  = "Premium, distinctive packaging that immediately conveys brand identity"
        brand = "Invest 20% of margin into brand content and SEO — create category authority"

    # ── Budget-based extras ─────────────────────────────────────────────────
    if budget >= 10000:
        tactics.append("Run a 7-day launch PPC campaign with 120% target ACoS to accumulate reviews fast")
    elif budget >= 3000:
        tactics.append("Allocate 15% of budget to sponsored product ads for first 30 days")
    else:
        tactics.append("Focus on organic SEO and social sharing — minimize paid spend initially")

    # ── Experience-based extras ─────────────────────────────────────────────
    if exp == "beginner":
        tactics.append("Join seller community forums (Seller Central, Reddit r/FulfillmentByAmazon) to learn fast")
    elif exp == "expert":
        tactics.append("Leverage existing brand/customer relationships for cross-sell opportunities")

    return DifferentiationStrategy(
        tactics           = tactics[:5],   # keep top 5
        bundle_suggestion = bundle,
        packaging_advice  = pack,
        brand_building_tip= brand,
    )
