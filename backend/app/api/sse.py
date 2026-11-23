"""
GuardDengue — Server-Sent Events (SSE) Stream Generator (Zone 5)

Streams real-time LangGraph execution milestones to the frontend:
  1. screener_triage: Zone 2 sub-20ms determination
  2. template_bypass: Immediate emergency / NSAID bypass
  3. retrieval_complete: Zone 4 evidence chunks and coverage
  4. verification_audit: Zone 5 claim NLI scores and conflicts
  5. answer_publish: Final verified answer release
  6. answer_abstain: Fallback clinical referral
"""
import asyncio
import json
import time
from typing import AsyncGenerator
from app.schemas.chat import ChatRequest
from app.schemas.state import DengueGraphState
from app.graph.nodes.screener_node import screener_node
from app.graph.nodes.urgent_node import urgent_node
from app.graph.nodes.medication_node import medication_node
from app.graph.nodes.retrieve_node import retrieve_node
from app.graph.nodes.draft_node import draft_node
from app.graph.nodes.verify_node import verify_node
from app.graph.nodes.publish_node import publish_node
from app.graph.nodes.abstain_node import abstain_node

from sse_starlette.sse import ServerSentEvent

def format_sse_chunk(event: str, data: dict) -> ServerSentEvent:
    """Formats a typed ServerSentEvent conforming to sse-starlette."""
    json_str = json.dumps(data, ensure_ascii=False)
    return ServerSentEvent(event=event, data=json_str, sep="\n")

async def stream_pipeline_events(req: ChatRequest) -> AsyncGenerator[ServerSentEvent, None]:
    """
    Executes the clinical pipeline step-by-step and streams semantic stage events.
    """
    start_total = time.perf_counter()
    session_id = req.session_id or f"sess_{int(time.time())}"
    language = req.language or "en"
    question = req.message

    state: DengueGraphState = {
        "session_id": session_id,
        "question": question,
        "language": language,
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

    # ── Step 1: Zone 2 Screener Node ─────────────────────────────────────────
    screener_updates = screener_node(state)
    state.update(screener_updates)

    yield format_sse_chunk(
        "screener_triage",
        {
            "route": state["route"],
            "matched_rules": state["matched_rules"],
            "intent": state["intent_description"],
            "dial_108": state.get("telephony_action") is not None,
            "latency_ms": state["zone2_latency_ms"],
            "node": "screener_node",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
    )
    await asyncio.sleep(0.01)

    # ── Immediate Deterministic Bypasses ─────────────────────────────────────
    if state["route"] == "urgent":
        urgent_updates = urgent_node(state)
        state.update(urgent_updates)

        yield format_sse_chunk(
            "template_bypass",
            {
                "route": "urgent",
                "verdict": "template_bypass",
                "answer": state["answer"],
                "telephony_action": state["telephony_action"],
                "safety_disclaimer": state["safety_disclaimer"],
                "evidence": [],
                "node": "urgent_node"
            }
        )
        total_latency = (time.perf_counter() - start_total) * 1000.0
        yield format_sse_chunk(
            "answer_publish",
            {
                "session_id": session_id,
                "route": state["route"],
                "verdict": state["verdict"],
                "answer": state["answer"],
                "evidence": [],
                "evidence_ok": True,
                "attempts": 0,
                "is_fallback": False,
                "safety_disclaimer": state["safety_disclaimer"],
                "matched_rules": state["matched_rules"],
                "telephony_action": state["telephony_action"],
                "verification_score": 1.0,
                "metrics": {
                    "total_latency_ms": round(total_latency, 2),
                    "zone2_screener_ms": state["zone2_latency_ms"],
                    "model_generation_ms": 0.0,
                    "nli_verification_ms": 0.0
                }
            }
        )
        return

    elif state["route"] == "medication":
        med_updates = medication_node(state)
        state.update(med_updates)

        yield format_sse_chunk(
            "template_bypass",
            {
                "route": "medication",
                "verdict": "template_bypass",
                "answer": state["answer"],
                "telephony_action": None,
                "safety_disclaimer": state["safety_disclaimer"],
                "evidence": [],
                "node": "medication_node"
            }
        )
        total_latency = (time.perf_counter() - start_total) * 1000.0
        yield format_sse_chunk(
            "answer_publish",
            {
                "session_id": session_id,
                "route": state["route"],
                "verdict": state["verdict"],
                "answer": state["answer"],
                "evidence": [],
                "evidence_ok": True,
                "attempts": 0,
                "is_fallback": False,
                "safety_disclaimer": state["safety_disclaimer"],
                "matched_rules": state["matched_rules"],
                "telephony_action": None,
                "verification_score": 1.0,
                "metrics": {
                    "total_latency_ms": round(total_latency, 2),
                    "zone2_screener_ms": state["zone2_latency_ms"],
                    "model_generation_ms": 0.0,
                    "nli_verification_ms": 0.0
                }
            }
        )
        return

    # ── Educational Route (Retrieval + Generation + Verification) ────────────
    elif state["route"] == "education":
        # 1. Retrieval
        ret_updates = retrieve_node(state)
        state.update(ret_updates)

        yield format_sse_chunk(
            "retrieval_complete",
            {
                "evidence_count": len(state["evidence"]),
                "coverage_status": state["coverage_status"],
                "evidence": state["evidence"],
                "latency_ms": state["retrieval_latency_ms"],
                "node": "retrieve_node"
            }
        )
        await asyncio.sleep(0.01)

        if not state["evidence_ok"]:
            abstain_updates = abstain_node(state)
            state.update(abstain_updates)
            total_latency = (time.perf_counter() - start_total) * 1000.0
            yield format_sse_chunk(
                "answer_abstain",
                {
                    "session_id": session_id,
                    "route": state["route"],
                    "verdict": "reject",
                    "answer": state["answer"],
                    "is_fallback": True,
                    "safety_disclaimer": state["safety_disclaimer"],
                    "reason": "insufficient_evidence",
                    "metrics": {
                        "total_latency_ms": round(total_latency, 2),
                        "zone2_screener_ms": state["zone2_latency_ms"],
                        "model_generation_ms": 0.0,
                        "nli_verification_ms": 0.0
                    }
                }
            )
            return

        # 2. Draft Generation
        draft_updates = draft_node(state)
        state.update(draft_updates)
        await asyncio.sleep(0.01)

        # 3. Claim Verification Gate
        verify_updates = verify_node(state)
        state.update(verify_updates)

        yield format_sse_chunk(
            "verification_audit",
            {
                "verdict": state["verdict"],
                "verification_score": state["verification_score"],
                "conflict_counts": state["conflict_counts"],
                "extracted_claims": state["extracted_claims"],
                "latency_ms": state["verification_latency_ms"],
                "node": "verify_node"
            }
        )
        await asyncio.sleep(0.01)

        # 4. Enforce Bounded Revision or Publish
        if state["verdict"] == "pass":
            pub_updates = publish_node(state)
            state.update(pub_updates)
            total_latency = (time.perf_counter() - start_total) * 1000.0

            yield format_sse_chunk(
                "answer_publish",
                {
                    "session_id": session_id,
                    "route": state["route"],
                    "verdict": state["verdict"],
                    "answer": state["answer"],
                    "evidence": state["evidence"],
                    "evidence_ok": True,
                    "attempts": state["attempts"],
                    "is_fallback": False,
                    "safety_disclaimer": state["safety_disclaimer"],
                    "matched_rules": state["matched_rules"],
                    "telephony_action": None,
                    "verification_score": state["verification_score"],
                    "extracted_claims": state["extracted_claims"],
                    "metrics": {
                        "total_latency_ms": round(total_latency, 2),
                        "zone2_screener_ms": state["zone2_latency_ms"],
                        "model_generation_ms": state["generation_latency_ms"],
                        "nli_verification_ms": state["verification_latency_ms"]
                    }
                }
            )
            return
        else:
            # Rejection or failed second attempt
            abstain_updates = abstain_node(state)
            state.update(abstain_updates)
            total_latency = (time.perf_counter() - start_total) * 1000.0

            yield format_sse_chunk(
                "answer_abstain",
                {
                    "session_id": session_id,
                    "route": state["route"],
                    "verdict": "reject",
                    "answer": state["answer"],
                    "is_fallback": True,
                    "safety_disclaimer": state["safety_disclaimer"],
                    "reason": "verification_failed",
                    "metrics": {
                        "total_latency_ms": round(total_latency, 2),
                        "zone2_screener_ms": state["zone2_latency_ms"],
                        "model_generation_ms": state["generation_latency_ms"],
                        "nli_verification_ms": state["verification_latency_ms"]
                    }
                }
            )
            return

    # ── Out of Scope Route ───────────────────────────────────────────────────
    else:
        abstain_updates = abstain_node(state)
        state.update(abstain_updates)
        total_latency = (time.perf_counter() - start_total) * 1000.0

        yield format_sse_chunk(
            "answer_abstain",
            {
                "session_id": session_id,
                "route": state["route"],
                "verdict": "reject",
                "answer": state["answer"],
                "is_fallback": True,
                "safety_disclaimer": state["safety_disclaimer"],
                "reason": "out_of_scope",
                "metrics": {
                    "total_latency_ms": round(total_latency, 2),
                    "zone2_screener_ms": state["zone2_latency_ms"],
                    "model_generation_ms": 0.0,
                    "nli_verification_ms": 0.0
                }
            }
        )
