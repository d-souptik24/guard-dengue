"""
GuardDengue — LangGraph Workflow Assembly & Compilation

Constructs the 5-zone clinical state machine connecting Zone 2 deterministic screening,
Zone 4 knowledge base retrieval, Zone 3 generative drafting, and Zone 5 claim verification.
"""
from langgraph.graph import END, StateGraph
from app.schemas.state import DengueGraphState

# Nodes
from app.graph.nodes.screener_node import screener_node
from app.graph.nodes.urgent_node import urgent_node
from app.graph.nodes.medication_node import medication_node
from app.graph.nodes.retrieve_node import retrieve_node
from app.graph.nodes.draft_node import draft_node
from app.graph.nodes.verify_node import verify_node
from app.graph.nodes.publish_node import publish_node
from app.graph.nodes.abstain_node import abstain_node

# Conditional Edges
from app.graph.edges import (
    route_after_screener,
    route_after_retrieve,
    route_after_verify,
)

def create_dengue_pipeline():
    """Builds and compiles the canonical GuardDengue LangGraph clinical pipeline."""
    builder = StateGraph(DengueGraphState)

    # 1. Register Nodes
    builder.add_node("screener_node", screener_node)
    builder.add_node("urgent_node", urgent_node)
    builder.add_node("medication_node", medication_node)
    builder.add_node("retrieve_node", retrieve_node)
    builder.add_node("draft_node", draft_node)
    builder.add_node("verify_node", verify_node)
    builder.add_node("publish_node", publish_node)
    builder.add_node("abstain_node", abstain_node)

    # 2. Set Entry Point
    builder.set_entry_point("screener_node")

    # 3. Connect Edges from Screener
    builder.add_conditional_edges(
        "screener_node",
        route_after_screener,
        {
            "urgent_node": "urgent_node",
            "medication_node": "medication_node",
            "retrieve_node": "retrieve_node",
            "abstain_node": "abstain_node",
        }
    )

    # 4. Immediate Terminal Bypasses
    builder.add_edge("urgent_node", END)
    builder.add_edge("medication_node", END)

    # 5. Connect Retrieval to Draft or Abstain
    builder.add_conditional_edges(
        "retrieve_node",
        route_after_retrieve,
        {
            "draft_node": "draft_node",
            "abstain_node": "abstain_node",
        }
    )

    # 6. Draft always goes to Verification Gate
    builder.add_edge("draft_node", "verify_node")

    # 7. Verification Gate Routes to Publish, Draft (revise), or Abstain
    builder.add_conditional_edges(
        "verify_node",
        route_after_verify,
        {
            "publish_node": "publish_node",
            "draft_node": "draft_node",
            "abstain_node": "abstain_node",
        }
    )

    # 8. Terminal endpoints
    builder.add_edge("publish_node", END)
    builder.add_edge("abstain_node", END)

    return builder.compile()

# Compile the singleton runnable workflow
clinical_pipeline = create_dengue_pipeline()
