"""
GuardDengue — LangGraph Node: Answer Publish (Zone 5)
"""
from typing import Any
from app.schemas.state import DengueGraphState

def publish_node(state: DengueGraphState) -> dict[str, Any]:
    trace_step = {
        "node": "publish_node",
        "action": "publish_verified_answer",
        "verdict": "pass",
        "score": state.get("verification_score", 1.0)
    }

    return {
        "answer": state.get("draft", ""),
        "is_fallback": False,
        "trace_steps": [trace_step],
    }
