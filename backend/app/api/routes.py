"""
GuardDengue — Core API Route Handlers

Provides:
  - POST /api/chat: One-shot JSON response from LangGraph clinical pipeline
  - POST /api/chat/stream: SSE event stream for live state progression
  - GET  /api/health & GET /health: Service readiness and health probe
  - POST /api/session: Session lifecycle initialization
"""
import time
import uuid
from fastapi import APIRouter, HTTPException, status
from sse_starlette.sse import EventSourceResponse

from app.core.config import settings
from app.schemas.chat import ChatRequest, ChatResponse, LatencyMetrics
from app.schemas.evidence import EvidenceChunk
from app.schemas.state import DengueGraphState
from app.graph.workflow import clinical_pipeline
from app.api.sse import stream_pipeline_events

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Synchronous one-shot chat endpoint executing the full LangGraph pipeline.
    """
    start_time = time.perf_counter()
    session_id = req.session_id or f"sess_{uuid.uuid4().hex[:8]}"

    initial_state: DengueGraphState = {
        "session_id": session_id,
        "question": req.message,
        "language": req.language or "en",
        "history": [{"role": m.role, "content": m.content} for m in req.history],
        "client_timestamp": req.client_timestamp,
        "route": "uncertain",
        "matched_rules": [],
        "intent_description": "",
        "zone2_latency_ms": 0.0,
        "evidence": [],
        "evidence_ok": False,
        "coverage_status": "unavailable",
        "retrieval_latency_ms": 0.0,
        "draft": "",
        "attempts": 0,
        "generation_latency_ms": 0.0,
        "verdict": "reject",
        "verification_score": 0.0,
        "conflict_counts": {},
        "extracted_claims": [],
        "verification_latency_ms": 0.0,
        "answer": "",
        "is_fallback": False,
        "safety_disclaimer": "",
        "telephony_action": None,
        "trace_steps": [],
        "token_usage": {},
    }

    try:
        final_state = clinical_pipeline.invoke(initial_state)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical pipeline failure: {str(e)}"
        )

    total_latency_ms = (time.perf_counter() - start_time) * 1000.0

    # Format evidence chunks
    evidence_models = []
    for item in final_state.get("evidence", []):
        try:
            evidence_models.append(EvidenceChunk(**item))
        except Exception:
            pass

    metrics = LatencyMetrics(
        total_latency_ms=round(total_latency_ms, 2),
        zone2_screener_ms=final_state.get("zone2_latency_ms", 0.0),
        model_generation_ms=final_state.get("generation_latency_ms", 0.0),
        nli_verification_ms=final_state.get("verification_latency_ms", 0.0)
    )

    return ChatResponse(
        session_id=session_id,
        route=final_state["route"],
        verdict=final_state["verdict"],
        evidence_ok=final_state.get("evidence_ok", True),
        attempts=final_state.get("attempts", 0),
        is_fallback=final_state.get("is_fallback", False),
        answer=final_state["answer"],
        evidence=evidence_models,
        safety_disclaimer=final_state.get("safety_disclaimer", ""),
        matched_rules=final_state.get("matched_rules", []),
        telephony_action=final_state.get("telephony_action"),
        verification_score=final_state.get("verification_score", 1.0),
        metrics=metrics
    )

@router.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    """
    Server-Sent Events endpoint streaming real-time intermediate state transitions.
    """
    return EventSourceResponse(
        stream_pipeline_events(req),
        media_type="text/event-stream"
    )

@router.get("/health")
async def health_check():
    """
    System health and readiness probe.
    """
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "corpus_release": settings.CORPUS_RELEASE,
        "slm_provider": settings.SLM_PROVIDER,
        "sqlite_storage": settings.SQLITE_DB_PATH.exists(),
        "qdrant_storage": settings.QDRANT_STORAGE_DIR.exists(),
        "policy_file": settings.POLICY_FILE_PATH.exists(),
    }

@router.post("/session")
async def session_endpoint():
    """Generates an ephemeral session ID with privacy compliance."""
    new_id = f"sess_{uuid.uuid4().hex[:12]}"
    return {"session_id": new_id, "status": "active", "created_at": time.time()}
