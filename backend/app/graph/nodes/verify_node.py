"""
GuardDengue — LangGraph Node: Claim Verification Gate (Zone 5)
"""
from typing import Any
from app.schemas.state import DengueGraphState
from app.verification.engine import verification_engine

def verify_node(state: DengueGraphState) -> dict[str, Any]:
    draft_text = state.get("draft", "")
    evidence = state.get("evidence", [])
    question = state.get("question", "")
    
    report = verification_engine.verify(
        draft_text=draft_text,
        evidence_chunks=evidence,
        user_question=question
    )

    trace_step = {
        "node": "verify_node",
        "verdict": report.verdict,
        "verification_score": report.verification_score,
        "conflict_counts": report.conflict_counts,
        "claim_count": len(report.extracted_claims),
        "violations": report.violations,
        "latency_ms": report.verification_latency_ms
    }

    return {
        "verdict": report.verdict,
        "verification_score": report.verification_score,
        "conflict_counts": report.conflict_counts,
        "extracted_claims": report.extracted_claims,
        "verification_latency_ms": report.verification_latency_ms,
        "trace_steps": [trace_step],
    }
