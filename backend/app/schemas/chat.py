"""
GuardDengue — Request, Response & SSE Streaming Event Schemas

Strictly aligned with docs/design/api_contract.md and frontend/src/types/index.ts.
"""
from typing import Any, Literal
from pydantic import BaseModel, Field
from app.schemas.evidence import EvidenceChunk

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    session_id: str | None = Field(default="sess_default")
    language: Literal["en", "bn"] = Field(default="en")
    history: list[ChatMessage] = Field(default_factory=list)
    client_timestamp: str | None = None

class LatencyMetrics(BaseModel):
    total_latency_ms: float = 0.0
    zone2_screener_ms: float = 0.0
    model_generation_ms: float = 0.0
    nli_verification_ms: float = 0.0

class ChatResponse(BaseModel):
    session_id: str
    route: str
    verdict: str
    evidence_ok: bool = True
    attempts: int = 0
    is_fallback: bool = False
    answer: str
    evidence: list[EvidenceChunk] = Field(default_factory=list)
    safety_disclaimer: str
    matched_rules: list[str] = Field(default_factory=list)
    telephony_action: dict[str, str] | None = None
    verification_score: float = 1.0
    metrics: LatencyMetrics = Field(default_factory=LatencyMetrics)

class StreamEvent(BaseModel):
    event: str
    data: dict[str, Any] = Field(default_factory=dict)
