"""
GuardDengue — FastAPI Application Entry Point

Mounts REST and SSE API routes, configures CORS, and serves the pre-compiled
production React 19 frontend from backend/static/.
"""
from contextlib import asynccontextmanager
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.routes import router as api_router

logger = logging.getLogger("guarddengue")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Corpus Release: {settings.CORPUS_RELEASE}")
    logger.info(f"SLM Provider: {settings.SLM_PROVIDER}")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Clinical Decision Support System & Dengue Triage Assistant",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Endpoints (/api/chat, /api/chat/stream, /api/health, /api/session)
app.include_router(api_router, prefix="/api")

# Also mount /health directly at root for load balancer / k8s probes
@app.get("/health")
async def root_health():
    from app.api.routes import health_check
    return await health_check()

# Mount Static Files (Pre-compiled React 19 Frontend)
if settings.STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(settings.STATIC_DIR), html=True), name="static")
    logger.info(f"Mounted static frontend from {settings.STATIC_DIR}")
else:
    logger.warning(f"Static directory not found at {settings.STATIC_DIR}")
