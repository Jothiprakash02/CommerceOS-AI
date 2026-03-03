"""
API Router — POST /profile  (Module 1)
=======================================
Collects the seller profile and returns a normalized config.
No market research at this phase.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from InputConfig.schemas.input_schema    import InputSchema
from InputConfig.schemas.response_schema import ProcessedConfig, ProfileResponse
from InputConfig.services.pipeline      import execute_pipeline

log    = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/profile",
    response_model=ProfileResponse,
    summary="Collect & configure seller profile",
    description=(
        "Phase 1: Accepts seller profile (niche, budget, risk level, country, experience). "
        "Validates, normalizes, and returns the structured personalization config. "
        "No market research is performed at this stage."
    ),
    tags=["Module 1 — Input Config"],
)
async def collect_profile(req: InputSchema) -> ProfileResponse:

    log.info(
        "POST /profile | niche='%s' country='%s' risk='%s' budget=%.0f exp='%s'",
        req.niche, req.country, req.risk_level, req.budget, req.experience,
    )

    try:
        result = execute_pipeline(req.dict())
    except Exception as exc:
        log.error("Profile pipeline failure: %s", exc, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Profile error: {exc}")

    return ProfileResponse(
        status  = result["status"],
        profile = ProcessedConfig(**result["profile"]),
        message = result.get("message"),
    )
