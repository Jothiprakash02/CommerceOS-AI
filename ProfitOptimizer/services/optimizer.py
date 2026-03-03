"""
Module 3 — Demand-Based Profit Optimization Engine
Implements the 7-step MPI formula to compute optimal price,
margin, inventory, and profit for a given product/market context.
"""

import sys
import os

# Ensure global/ utils are accessible
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", "..", "global"))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from utils.normalizer import clamp
from ProfitOptimizer.schemas.optimization_schema import OptimizationInput, OptimizationResult


def optimize_profit(inp: OptimizationInput) -> OptimizationResult:
    """
    7-step optimization pipeline:
      1. Normalize demand & competition scores.
      2. Compute Market Power Index (MPI).
      3. Derive dynamic margin from MPI.
      4. Calculate optimal selling price.
      5. Apply price elasticity to volume.
      6. Compute unit profit & monthly profit.
      7. Recommend inventory within budget.
    """

    # ── Step 1 & 2: Market Power Index ─────────────────────────────────────
    normalized_demand      = inp.demand_score / 100.0
    normalized_competition = inp.competition_score / 100.0
    mpi = (normalized_demand * 0.6) + ((1.0 - normalized_competition) * 0.4)
    mpi = round(clamp(mpi, 0.0, 1.0), 4)

    # ── Step 3: Dynamic margin ──────────────────────────────────────────────
    margin_adjustment = (mpi - 0.5) * 0.2
    final_margin = clamp(inp.base_margin + margin_adjustment, 0.18, 0.40)
    final_margin = round(final_margin, 4)

    # ── Step 4: Optimal selling price ──────────────────────────────────────
    # effective_fee = platform fee (country_fee) + assumed ad-spend (10%)
    effective_fee = inp.country_fee + 0.10
    denominator = 1.0 - final_margin - effective_fee
    if denominator <= 0:
        denominator = 0.01           # safety guard against degenerate inputs
    selling_price = inp.cost_per_unit / denominator
    selling_price = round(selling_price, 2)

    # ── Step 5: Price-elasticity-adjusted volume ────────────────────────────
    price_elasticity_factor = 1.0 - ((final_margin - 0.25) * 0.5)
    price_elasticity_factor = clamp(price_elasticity_factor, 0.5, 1.5)
    adjusted_volume = int(round(inp.estimated_sales * price_elasticity_factor))

    # ── Step 6: Profit calculations ─────────────────────────────────────────
    unit_profit   = selling_price - inp.cost_per_unit - (selling_price * effective_fee)
    unit_profit   = round(unit_profit, 2)
    monthly_profit = round(unit_profit * adjusted_volume, 2)

    # ── Step 7: Recommended inventory ──────────────────────────────────────
    budget_units = int(inp.budget / inp.cost_per_unit) if inp.cost_per_unit > 0 else 0
    recommended_inventory = int(min(adjusted_volume * 1.2, budget_units))

    # ── Risk classification ─────────────────────────────────────────────────
    if mpi > 0.7:
        risk_level = "Low"
    elif mpi >= 0.5:
        risk_level = "Moderate"
    else:
        risk_level = "High"

    return OptimizationResult(
        market_power_index   = mpi,
        final_margin         = final_margin,
        selling_price        = selling_price,
        unit_profit          = unit_profit,
        adjusted_volume      = adjusted_volume,
        monthly_profit       = monthly_profit,
        recommended_inventory= recommended_inventory,
        risk_level           = risk_level,
    )
