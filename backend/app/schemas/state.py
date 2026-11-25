"""
GuardDengue — Canonical LangGraph GraphState TypedDict

Synchronized with Plan Version 2 and frontend/src/types/index.ts.
"""
from typing import Annotated, Any, Literal, TypedDict
import operator

# The 4 canonical routes from the Architecture Review
RouteType = Literal["urgent", "medication", "education", "uncertain"]

# Verdict outcomes from the Claim Verification Gate
VerdictType = Literal["pass", "revise", "reject", "template_bypass"]

class DengueGraphState(TypedDict):
    """
    Mutable state object passed between nodes in the LangGraph clinical pipeline.
    """
    # ─── 1. Inbound Citizen Query & Context ──────────────────────────────────
    session_id: str
    question: str
    language: Literal["en", "bn"]
    history: list[dict[str, str]]
    client_timestamp: str | None
    
    # ─── 2. Zone 2 Screener & Route Assignment ───────────────────────────────
    route: RouteType
    matched_rules: list[str]
    intent_description: str
    zone2_latency_ms: float
    
    # ─── 3. Zone 4 Knowledge Base Retrieval ───────────────────────────────────
    evidence: list[dict[str, Any]]
    evidence_ok: bool
    coverage_status: Literal["complete", "partial", "unavailable"]
    retrieval_latency_ms: float
    
    # ─── 4. Zone 3 Draft Generation & Bounded Revision Loop ───────────────────
    draft: str
    attempts: int                   # Initialized to 0; maximum 2 attempts before abstention
    generation_latency_ms: float
    
    # ─── 5. Zone 5 Claim Verification & Basu & Huynh Audit ───────────────────
    verdict: VerdictType
    verification_score: float       # NLI cross-encoder confidence score [0, 1]
    conflict_counts: dict[str, int] # {"input_conflicts": 0, "context_conflicts": 0, "fact_conflicts": 0}
    extracted_claims: list[str]
    verification_latency_ms: float
    
    # ─── 6. Final Certified Output & Telemetry ───────────────────────────────
    answer: str
    is_fallback: bool
    safety_disclaimer: str
    telephony_action: dict[str, str] | None
    
    # ─── 7. Observability Stream Events (Accumulated for Inspector) ──────────
    trace_steps: Annotated[list[dict[str, Any]], operator.add]
    token_usage: dict[str, int]     # {"prompt_tokens": 0, "completion_tokens": 0, "thinking_tokens": 0}
