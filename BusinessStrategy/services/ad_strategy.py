"""
Ad Strategy Generator — Module 4 Submodule 5
Creates platform-specific ad angles and offer strategy.
"""
from BusinessStrategy.schemas.strategy_schema import AdStrategy, StrategyInput


def run_ad_strategy(inp: StrategyInput) -> AdStrategy:
    niche   = inp.niche.title()
    price   = inp.selling_price
    sym     = inp.currency_symbol
    dem     = inp.demand_score
    comp    = inp.competition_score
    trend   = inp.trend_direction
    volume  = inp.adjusted_volume
    budget  = inp.budget
    risk    = inp.risk_level

    # ── Facebook hook ────────────────────────────────────────────────────────
    if comp > 65:
        fb_hook = (f"Tired of overpriced {niche} that breaks in 3 months? "
                   f"We built a better one at {sym}{price:.0f} — and 1,000+ customers agree.")
    elif dem > 65:
        fb_hook = (f"🔥 {niche} is trending RIGHT NOW — and most sellers are out of stock. "
                   f"We're not. Get yours at {sym}{price:.0f} before we run out.")
    else:
        fb_hook = (f"This {niche} changed how I work every day. "
                   f"Under {sym}{price:.0f}. Limited stock.")

    # ── Instagram reel concept ───────────────────────────────────────────────
    if trend in ("rising", "stable"):
        ig_concept = (f"30-second 'unboxing to first use' reel for {niche}. "
                      "Hook: show the problem in 3 seconds, reveal the product as the fix. "
                      "End with price tag close-up. Add trending audio.")
    else:
        ig_concept = (f"Side-by-side comparison reel: competitor {niche} vs yours. "
                      "Highlight quality difference visually. No talking, only text overlays.")

    # ── Google ad copy ───────────────────────────────────────────────────────
    google_copy = (f"Best {niche} Under {sym}{price:.0f} | Fast Delivery | "
                   f"{'Top Rated' if comp > 50 else 'Premium Quality'} | Shop Now")

    # ── Offer strategy ───────────────────────────────────────────────────────
    launch_units = min(int(volume * 0.25), 200)
    if risk == "aggressive":
        offer = (f"Flash launch: {sym}{price * 0.85:.0f} for first {launch_units} buyers "
                 f"(15% off), then restore to {sym}{price:.0f}. Creates urgency + review velocity.")
    elif risk == "moderate":
        offer = (f"Early bird: first {launch_units} units at {sym}{price * 0.90:.0f} "
                 f"(10% off). Countdown timer on listing. Valid 7 days only.")
    else:
        offer = (f"Value bundle: add a low-cost accessory (worth {sym}{price * 0.10:.0f}) "
                 "free with purchase for first 30 days. Protects margin while driving conversions.")

    # ── Content angle ────────────────────────────────────────────────────────
    if inp.market_power_index > 0.65:
        angle = (f"Authority content: '5 things to check before buying {niche}' — "
                 "positions your brand as the expert and your product as the obvious choice.")
    else:
        angle = (f"Problem-solution story: 'I was frustrated with every {niche} I tried — "
                 "until I built my own criteria.' Ends with your product as the solution.")

    return AdStrategy(
        facebook_hook     = fb_hook,
        instagram_concept = ig_concept,
        google_ad_copy    = google_copy,
        offer_strategy    = offer,
        content_angle     = angle,
    )
