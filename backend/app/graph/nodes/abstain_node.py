"""
GuardDengue — LangGraph Node: Abstain / Clinical Referral (Zone 5)
"""
from typing import Any
from app.schemas.state import DengueGraphState
from app.safety.templates import ABSTAIN_UNCERTAIN_BN, ABSTAIN_UNCERTAIN_EN

def abstain_node(state: DengueGraphState) -> dict[str, Any]:
    language = state.get("language", "en")
    answer = ABSTAIN_UNCERTAIN_BN if language == "bn" else ABSTAIN_UNCERTAIN_EN
    
    trace_step = {
        "node": "abstain_node",
        "action": "answer_abstain",
        "verdict": "reject",
        "reason": "Max revision attempts exhausted or query out-of-scope; triggered safe clinical referral."
    }

    return {
        "verdict": "reject",
        "answer": answer,
        "is_fallback": True,
        "trace_steps": [trace_step],
    }
