"""
Profile Pipeline — Module 1
============================
Collects, validates and normalizes the seller profile.
No market research happens here — this phase is purely about
understanding WHO the user is and WHAT constraints they have.

The resulting ProcessedConfig is returned and can later be
passed to Module 2 when market analysis is triggered.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from InputConfig.services.input_processor import process_user_input

log = logging.getLogger(__name__)


def execute_pipeline(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phase 1 pipeline — profile collection only.

    Steps:
      1. Normalize and enrich user input
      2. Return structured profile config

    No API calls. No scraping. No LLM.

    Returns:
        {
          "status":  "configured",
          "profile": {...},
          "message": str
        }
    """
    log.info(
        "Profile collection — niche='%s' budget=%.0f risk='%s' country='%s' exp='%s'",
        input_data.get("niche"), input_data.get("budget"),
        input_data.get("risk_level"), input_data.get("country"),
        input_data.get("experience"),
    )

    profile = process_user_input(input_data)

    log.info("Profile configured — effective_budget=%.0f platform='%s'",
             profile["effective_budget"], profile["platform"])

    return {
        "status":  "configured",
        "profile": profile,
        "message": (
            f"Profile saved. Ready to analyze '{profile['niche']}' "
            f"on {profile['platform']} with {profile['currency_symbol']}"
            f"{profile['effective_budget']:,.0f} effective budget."
        ),
    }
