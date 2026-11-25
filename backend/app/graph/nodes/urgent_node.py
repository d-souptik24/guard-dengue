"""
GuardDengue — LangGraph Node: Urgent Red Flag Bypass (Zone 2)
"""
from typing import Any
from app.schemas.state import DengueGraphState
from app.safety.templates import EMERGENCY_RED_FLAG_BN, EMERGENCY_RED_FLAG_EN

def urgent_node(state: DengueGraphState) -> dict[str, Any]:
    language = state.get("language", "en")
    answer = state.get("answer") or (EMERGENCY_RED_FLAG_BN if language == "bn" else EMERGENCY_RED_FLAG_EN)
    
    trace_step = {
        "node": "urgent_node",
        "action": "template_bypass",
        "verdict": "template_bypass",
        "telephony": "108",
        "reason": "Emergency warning sign detected; bypassed generative inference."
    }

    return {
        "verdict": "template_bypass",
        "answer": answer,
        "is_fallback": False,
        "evidence": [],
        "evidence_ok": True,
        "coverage_status": "complete",
        "verification_score": 1.0,
        "conflict_counts": {"input_conflicts": 0, "context_conflicts": 0, "fact_conflicts": 0},
        "telephony_action": {
            "type": "tel_prompt",
            "number": "108",
            "label": "Call 108 Emergency Ambulance" if language == "en" else "১০৮ এম্বুলেন্সে কল করুন"
        },
        "trace_steps": [trace_step],
    }
