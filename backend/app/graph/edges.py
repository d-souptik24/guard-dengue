"""
GuardDengue — LangGraph Conditional Edges & Routing Logic
"""
from typing import Literal
from app.schemas.state import DengueGraphState

def route_after_screener(
    state: DengueGraphState
) -> Literal["urgent_node", "medication_node", "retrieve_node", "abstain_node"]:
    """Routes execution based on Zone 2 triage determination."""
    route = state.get("route", "uncertain")
    if route == "urgent":
        return "urgent_node"
    elif route == "medication":
        return "medication_node"
    elif route == "education":
        return "retrieve_node"
    else:
        return "abstain_node"

def route_after_retrieve(
    state: DengueGraphState
) -> Literal["draft_node", "abstain_node"]:
    """Routes to generation if guideline evidence exists, otherwise abstains."""
    if state.get("evidence_ok", False):
        return "draft_node"
    return "abstain_node"

def route_after_verify(
    state: DengueGraphState
) -> Literal["publish_node", "draft_node", "abstain_node"]:
    """
    Enforces the Bounded Revision Loop (max 2 attempts).
    If verification passes -> publish_node
    If verification requests revision and attempts < 2 -> draft_node
    Otherwise -> abstain_node
    """
    verdict = state.get("verdict", "reject")
    attempts = state.get("attempts", 0)

    if verdict == "pass":
        return "publish_node"
    elif verdict == "revise" and attempts < 2:
        return "draft_node"
    else:
        return "abstain_node"
