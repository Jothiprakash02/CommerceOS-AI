"""
Listing Content Generator — Module 4 Submodule 4
Uses Llama3 via Ollama to generate Amazon-style SEO listing content.
Falls back to rule-based generation if Ollama is unavailable.
"""
from __future__ import annotations
import json
import logging
import re
import sys
import os

log = logging.getLogger(__name__)

# Ensure global/ config is accessible
_GLOBAL = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "global"))
if _GLOBAL not in sys.path:
    sys.path.insert(0, _GLOBAL)

try:
    from config import OLLAMA_BASE_URL, OLLAMA_MODEL
except ImportError:
    OLLAMA_BASE_URL = "http://localhost:11434"
    OLLAMA_MODEL    = "llama3:8b"

from BusinessStrategy.schemas.strategy_schema import (
    ListingContent, StrategyInput, PositioningResult, AudienceProfile
)

_SYSTEM_PROMPT = """\
You are an expert Amazon product listing copywriter and SEO specialist.
Respond ONLY with valid JSON — no markdown, no explanations outside JSON.

Your response must contain exactly these keys:
{
  "seo_title": "<keyword-rich title, 150-200 chars, include brand placeholder, key feature, audience>",
  "bullet_points": [
    "✅ <benefit 1 — lead with strongest benefit>",
    "✅ <benefit 2>",
    "✅ <benefit 3>",
    "✅ <benefit 4>",
    "✅ <benefit 5 — end with guarantee or trust signal>"
  ],
  "product_description": "<2-3 paragraph persuasive description, 150-200 words, story-led, ends with CTA>",
  "cta": "<single sentence call-to-action>",
  "backend_keywords": ["<keyword1>", "<keyword2>", "<keyword3>", "<keyword4>", "<keyword5>"]
}
"""


def _build_prompt(inp: StrategyInput, pos: PositioningResult, aud: AudienceProfile) -> str:
    return f"""Generate an Amazon product listing for the following product:

Product: {inp.niche}
Selling Price: {inp.currency_symbol}{inp.selling_price:.0f}
Target Audience: {aud.primary_audience}
Positioning: {pos.positioning_type} — {pos.core_message}
Tone: {pos.tone}
Key Pain Points solved: {", ".join(aud.pain_points[:3])}
Buying Motivators: {", ".join(aud.buying_motivators[:3])}
Market Trend: {inp.trend_direction}
Country: {inp.country}

Write a compelling, SEO-optimized Amazon listing that converts browsers into buyers."""


def _call_ollama(prompt: str) -> dict | None:
    try:
        import requests
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            "stream": False,
        }
        resp = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        content = resp.json()["message"]["content"].strip()
        # Strip markdown code fences if present
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        return json.loads(content)
    except Exception as exc:
        log.warning("Ollama listing call failed: %s", exc)
        return None


def _rule_based_fallback(inp: StrategyInput, pos: PositioningResult, aud: AudienceProfile) -> ListingContent:
    """Structured fallback when Ollama is unavailable."""
    niche   = inp.niche.title()
    sym     = inp.currency_symbol
    price   = inp.selling_price
    trend   = inp.trend_direction.capitalize()
    audience= aud.primary_audience.split("aged")[0].strip()

    title = (f"{niche} — {pos.positioning_type} Quality | Perfect for {audience} | "
             f"{sym}{price:.0f} | {inp.country} | Fast Delivery | Trusted Brand")
    title = title[:200]

    bullets = [
        f"✅ ENGINEERED FOR PERFORMANCE — Built specifically for {audience.lower()} "
        f"who demand reliable {niche.lower()} without overpaying",
        f"✅ SOLVES YOUR BIGGEST FRUSTRATION — Addresses {aud.pain_points[0]} "
        f"that customers hate about competitor products",
        f"✅ {pos.tone.upper()} QUALITY GUARANTEE — Every unit rigorously tested before shipping. "
        f"We stand behind our product with full after-sales support",
        f"✅ TRENDING MARKET CHOICE — {trend} demand signals this is the right time to own "
        f"the best {niche.lower()} at {sym}{price:.0f}",
        f"✅ 30-DAY HASSLE-FREE RETURNS — Order with complete confidence. "
        f"Not satisfied? Full refund, no questions asked",
    ]

    description = (
        f"Introducing the {niche} built for {audience.lower()} — a product designed "
        f"from the ground up to solve {aud.pain_points[0].lower()} and deliver "
        f"{aud.buying_motivators[0].lower()}'.\n\n"
        f"Priced at {sym}{price:.0f}, this is the {pos.positioning_type.lower()} choice "
        f"for anyone who refuses to compromise on quality. Available now in {inp.country} "
        f"with fast, reliable delivery.\n\n"
        f"Join thousands of satisfied customers. Add to cart today — stock is limited."
    )

    cta = f"Click 'Add to Cart' now and experience {niche.lower()} the way it was meant to be."

    keywords = [
        inp.niche.lower(),
        f"best {inp.niche.lower()}",
        f"{inp.niche.lower()} {inp.country.lower()}",
        f"buy {inp.niche.lower()} online",
        f"affordable {inp.niche.lower()}",
    ] + [kw.lower() for kw in inp.top_keywords[:3]]

    return ListingContent(
        seo_title          = title,
        bullet_points      = bullets,
        product_description= description,
        cta                = cta,
        backend_keywords   = list(dict.fromkeys(keywords))[:8],
    )


def generate_listing(
    inp: StrategyInput,
    positioning: PositioningResult,
    audience: AudienceProfile,
) -> ListingContent:
    prompt = _build_prompt(inp, positioning, audience)
    data   = _call_ollama(prompt)

    if data:
        try:
            bullets = data.get("bullet_points", [])
            if len(bullets) < 5:
                bullets += [f"✅ Quality guaranteed — {inp.niche.title()} built to last"] * (5 - len(bullets))
            return ListingContent(
                seo_title          = str(data.get("seo_title", ""))[:200],
                bullet_points      = bullets[:5],
                product_description= str(data.get("product_description", "")),
                cta                = str(data.get("cta", "")),
                backend_keywords   = data.get("backend_keywords", [])[:8],
            )
        except Exception as exc:
            log.warning("Failed to parse Ollama listing output: %s", exc)

    log.info("Using rule-based listing fallback")
    return _rule_based_fallback(inp, positioning, audience)
