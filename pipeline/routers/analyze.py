"""
Pipeline router — POST /analyze
Single endpoint that runs the full M1 → M2 → M3 chain.
"""

from fastapi import APIRouter, HTTPException
from pipeline.schemas.pipeline_schema import PipelineRequest, PipelineResponse
from pipeline.services.full_pipeline  import run_full_pipeline

router = APIRouter()


@router.post("/analyze", response_model=PipelineResponse)
async def analyze(request: PipelineRequest):
    try:
        result = run_full_pipeline(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
