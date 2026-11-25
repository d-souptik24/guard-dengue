"""
GuardDengue — LangGraph Node: Knowledge Base Retrieval (Zone 4)
"""
from typing import Any
from app.schemas.state import DengueGraphState
from app.retrieval.engine import retrieval_engine

def retrieve_node(state: DengueGraphState) -> dict[str, Any]:
    chunks, ok, coverage, latency = retrieval_engine.retrieve(state["question"], top_k=4)
    
    serialized_chunks = [chunk.model_dump() for chunk in chunks]
    
    trace_step = {
        "node": "retrieve_node",
        "evidence_count": len(chunks),
        "evidence_ok": ok,
        "coverage_status": coverage,
        "latency_ms": latency
    }

    return {
        "evidence": serialized_chunks,
        "evidence_ok": ok,
        "coverage_status": coverage,
        "retrieval_latency_ms": latency,
        "trace_steps": [trace_step],
    }
