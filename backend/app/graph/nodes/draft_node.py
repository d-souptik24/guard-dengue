"""
GuardDengue — LangGraph Node: SLM Clinical Draft Generation (Zone 3)
"""
from typing import Any
from app.schemas.state import DengueGraphState
from app.models.factory import slm_provider

SYSTEM_PROMPT = (
    "You are GuardDengue, an expert Clinical Decision Support assistant for dengue fever in West Bengal, India. "
    "Provide clear, grounded advice strictly based on the provided WHO, ICMR, and NCVBDC guidelines. "
    "Never recommend NSAIDs (such as Aspirin, Ibuprofen, Combiflam, Diclofenac). "
    "Always emphasize physician consultation for high-risk signs."
)

def draft_node(state: DengueGraphState) -> dict[str, Any]:
    evidence_texts = []
    for c in state.get("evidence", []):
        content = c.get("content", "")
        meta = c.get("metadata", {})
        source = meta.get("source", "Guideline")
        evidence_texts.append(f"[{source}]: {content}")
        
    context_str = "\n\n".join(evidence_texts)
    
    prompt = (
        f"User Clinical Question: {state['question']}\n\n"
        f"Official Guideline Context:\n{context_str}\n\n"
        f"Provide a clinically rigorous, empathetic, and grounded response."
    )
    
    attempts = state.get("attempts", 0) + 1
    result = slm_provider.generate(prompt=prompt, system_prompt=SYSTEM_PROMPT)

    trace_step = {
        "node": "draft_node",
        "attempt": attempts,
        "model": result.model_name,
        "completion_tokens": result.completion_tokens,
        "thinking_tokens": result.thinking_tokens,
        "latency_ms": result.latency_ms,
        "thinking_trace": result.thinking_trace
    }

    token_usage = {
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "thinking_tokens": result.thinking_tokens
    }

    return {
        "draft": result.text,
        "attempts": attempts,
        "generation_latency_ms": result.latency_ms,
        "token_usage": token_usage,
        "trace_steps": [trace_step],
    }
