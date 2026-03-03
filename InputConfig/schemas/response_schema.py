"""
Response Schema — Module 1
==========================
Returns the normalized seller profile config.
No market research happens at this phase.
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class ProcessedConfig(BaseModel):
    """Normalized config derived from user input."""
    niche:             str
    budget:            float
    risk_level:        str
    risk_multiplier:   float
    target_margin:     float
    country_fee:       float
    country:           str
    platform:          str
    currency_symbol:   str
    experience:        str
    effective_budget:  float   # budget * risk_multiplier


class ProfileResponse(BaseModel):
    """Response returned after profile collection (Module 1)."""
    status:   str             # "configured"
    profile:  ProcessedConfig
    message:  Optional[str] = None
