"""
Target Audience Generator — Module 4 Submodule 2
Derives audience segments and pain-points from niche + market signals.
"""
from __future__ import annotations
from BusinessStrategy.schemas.strategy_schema import AudienceProfile, StrategyInput

# ── Niche keyword → audience heuristics ─────────────────────────────────────
_NICHE_MAP: dict[str, dict] = {
    "earbuds":      {"primary": "Students & commuters aged 18-30",  "secondary": "Remote workers",    "age": "18-30", "pain": ["poor sound quality", "tangled wires", "low battery life"],     "buy": ["sound clarity", "long battery", "wireless freedom"]},
    "headphone":    {"primary": "Music enthusiasts aged 16-35",     "secondary": "Gamers",            "age": "16-35", "pain": ["uncomfortable fit", "poor bass", "short cable"],               "buy": ["immersive audio", "comfort", "noise cancellation"]},
    "phone":        {"primary": "Tech-savvy adults aged 20-35",     "secondary": "First-time buyers", "age": "20-40", "pain": ["high cost", "short lifespan", "poor camera"],                  "buy": ["camera quality", "battery life", "brand value"]},
    "bag":          {"primary": "College students aged 18-24",      "secondary": "Working women",     "age": "18-35", "pain": ["poor durability", "limited compartments", "looks cheap"],     "buy": ["style", "durability", "storage capacity"]},
    "bottle":       {"primary": "Fitness enthusiasts aged 20-35",   "secondary": "Office workers",   "age": "18-40", "pain": ["leakage", "plastic taste", "short insulation"],                "buy": ["leak-proof", "BPA-free", "insulation duration"]},
    "watch":        {"primary": "Professionals aged 25-45",         "secondary": "Gift buyers",       "age": "22-45", "pain": ["poor battery", "non-stylish design", "low accuracy"],         "buy": ["style", "smart features", "battery life"]},
    "keyboard":     {"primary": "Programmers & gamers aged 18-35",  "secondary": "Office workers",   "age": "18-35", "pain": ["mushy keys", "poor build", "no backlight"],                    "buy": ["tactile feel", "durability", "RGB lighting"]},
    "lamp":         {"primary": "Students & home workers aged 18-40","secondary": "Interior buyers", "age": "18-40", "pain": ["eye strain", "high electricity", "ugly design"],               "buy": ["warm lighting", "energy saving", "aesthetics"]},
    "shoes":        {"primary": "Active adults aged 18-35",         "secondary": "Casual shoppers",  "age": "16-40", "pain": ["poor cushioning", "short durability", "narrow fit"],           "buy": ["comfort", "durability", "style"]},
    "shirt":        {"primary": "Young professionals aged 22-35",   "secondary": "College students", "age": "18-35", "pain": ["poor fabric quality", "sizing issues", "fading color"],       "buy": ["fabric quality", "fit", "versatility"]},
}

_DEFAULT = {
    "primary":   "General consumers aged 20-40",
    "secondary": "Gift buyers and repeat purchasers",
    "age":       "20-40",
    "pain":      ["high price", "low quality from competitors", "poor after-sales support"],
    "buy":       ["value for money", "reliable quality", "good reviews"],
}


def run_audience(inp: StrategyInput) -> AudienceProfile:
    niche_lower = inp.niche.lower()
    # fuzzy match on niche keywords
    matched = _DEFAULT
    for key, val in _NICHE_MAP.items():
        if key in niche_lower:
            matched = val
            break

    # Adjust by country if needed
    country_suffix = {
        "IN": " in India",
        "US": " in the US",
        "UK": " in the UK",
        "DE": " in Germany",
        "CA": " in Canada",
        "AU": " in Australia",
    }.get(inp.country, "")

    # Adjust by demand/competition
    extra_pain: list[str] = []
    if inp.competition_score > 65:
        extra_pain.append("overwhelmed by too many similar options")
    if inp.demand_score > 70:
        extra_pain.append("struggling to find products in stock")

    return AudienceProfile(
        primary_audience  = matched["primary"] + country_suffix,
        secondary_audience= matched["secondary"],
        age_range         = matched["age"],
        pain_points       = (matched["pain"] + extra_pain)[:4],
        buying_motivators = matched["buy"],
    )
