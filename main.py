"""
Product & Market Intelligence Engine
=====================================
FastAPI application entry point.

Run locally:
    uvicorn main:app --reload --port 8000

Docs:
    http://localhost:8000/docs
"""

import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()   # load .env file before anything else reads os.getenv()

# ─────────────────────────────────────────────
#  Path setup — make sub-folders importable
# ─────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _BASE)                                    # InputConfig package root
sys.path.insert(0, os.path.join(_BASE, "global"))           # config, database, utils
sys.path.insert(0, os.path.join(_BASE, "AiMarketResearch"))  # services, routers, models

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers.analyze import router as analyze_router
from InputConfig.routers.analyze import router as input_router
from pipeline.routers.analyze import router as pipeline_router
from TrendScout.routers.discover import router as trend_router
from BusinessStrategy.routers.strategy import router as strategy_router
from AiAssistant.routers.chat import router as chat_router
from ContentGenerator.routers.content import router as content_router

# 'global' is a reserved Python keyword — load via importlib
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("global_settings", os.path.join(_BASE, "global", "routers", "settings.py"))
_mod  = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
settings_router = _mod.router

# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# ─────────────────────────────────────────────
#  App
# ─────────────────────────────────────────────
app = FastAPI(
    title="MarketMind AI — Autonomous Product Discovery & Launch Intelligence",
    description=(
        "End-to-end AI market research platform for e-commerce sellers. "
        "Module 0: Global Trend Scouting Engine (NEW). "
        "Module 1: Input configuration & pipeline orchestration. "
        "Module 2: Real-time market signals, scoring, profit simulation & LLM strategy. "
        "Module 3: Demand-Based Profit Optimization Engine."
    ),
    version="4.0.0",
    contact={"name": "MarketMind AI — Hackathon Build"},
)

# ─────────────────────────────────────────────
#  CORS (open for hackathon / restrict in prod)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────
app.include_router(trend_router,    tags=["Module 0 — Trend Scouting"])  # POST /discover-trends
app.include_router(pipeline_router, tags=["Full Pipeline"])              # POST /analyze
app.include_router(input_router,    tags=["Module 1 — Input Config"])    # POST /profile
app.include_router(analyze_router,  tags=["Module 2 — Intelligence"])    # POST /analyze-product
app.include_router(strategy_router, tags=["Module 4 — Business Strategy"]) # POST /strategy
app.include_router(chat_router,     tags=["AI Assistant"])               # POST /chat
app.include_router(content_router,  tags=["Content Generator"])          # POST /generate-content
app.include_router(settings_router, tags=["System"])                     # GET/PUT /settings

# ─────────────────────────────────────────────
#  Frontend
#  /      → Full Pipeline UI  (pipeline)
#  /m1    → Module 1 UI      (InputConfig)
#  /ui    → Module 2 UI      (AiMarketResearch)
# ─────────────────────────────────────────────
_M1_FRONTEND  = os.path.join(_BASE, "InputConfig",      "frontend")
_M2_FRONTEND  = os.path.join(_BASE, "AiMarketResearch", "frontend")
_PL_FRONTEND  = os.path.join(_BASE, "pipeline",         "frontend")

if os.path.isdir(_M2_FRONTEND):
    app.mount("/ui", StaticFiles(directory=_M2_FRONTEND, html=True), name="m2_frontend")

if os.path.isdir(_M1_FRONTEND):
    app.mount("/m1", StaticFiles(directory=_M1_FRONTEND, html=True), name="m1_frontend")


@app.get("/", include_in_schema=False)
async def serve_pipeline_frontend():
    index = os.path.join(_PL_FRONTEND, "index.html")
    if os.path.exists(index):
        return FileResponse(index, media_type="text/html")
    return {"message": "CommerceOS AI API", "docs": "/docs"}


# ─────────────────────────────────────────────
#  Startup event
# ─────────────────────────────────────────────
@app.on_event("startup")
async def on_startup() -> None:
    init_db()
    logging.getLogger(__name__).info("Database initialized. Server ready.")


# ─────────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "service": "Product Intelligence Engine"}


# ─────────────────────────────────────────────
#  Dev entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
