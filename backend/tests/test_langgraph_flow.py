"""
GuardDengue — Integration Tests: LangGraph Clinical State Machine

Tests end-to-end execution paths across:
1. Urgent Red Flag Emergency Route (Deterministic Bypass)
2. Medication NSAID Intercept Route (Deterministic Bypass)
3. Educational RAG Route (SLM Generation -> Zone 5 Verification -> Publish)
4. Out-of-Scope Route (Abstain & Safe Clinical Referral)
"""
import pytest
from app.graph.workflow import clinical_pipeline
from app.schemas.state import DengueGraphState

def test_pipeline_urgent_red_flag_bypass():
    initial_state: DengueGraphState = {
        "session_id": "test_urgent_001",
        "question": "Patient has severe abdominal pain and vomiting blood with high fever",
        "language": "en",
        "history": [],
        "client_timestamp": None,
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

    final_state = clinical_pipeline.invoke(initial_state)

    assert final_state["route"] == "urgent"
    assert final_state["verdict"] == "template_bypass"
    assert final_state["telephony_action"] is not None
    assert final_state["telephony_action"]["number"] == "108"
    assert "EMERGENCY WARNING" in final_state["answer"]
    assert final_state["attempts"] == 0  # Zero generative attempts, direct bypass
    node_names = [t.get("node") for t in final_state["trace_steps"]]
    assert "screener_node" in node_names
    assert "urgent_node" in node_names
    assert "draft_node" not in node_names

def test_pipeline_medication_nsaid_bypass():
    initial_state: DengueGraphState = {
        "session_id": "test_med_002",
        "question": "Can I take Combiflam for fever and headache in dengue?",
        "language": "en",
        "history": [],
        "client_timestamp": None,
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

    final_state = clinical_pipeline.invoke(initial_state)

    assert final_state["route"] == "medication"
    assert final_state["verdict"] == "template_bypass"
    assert "Combiflam" in final_state["answer"]
    assert "strictly contraindicated" in final_state["answer"].lower()
    assert "Paracetamol" in final_state["answer"]
    assert final_state["attempts"] == 0

def test_pipeline_educational_rag_publish():
    initial_state: DengueGraphState = {
        "session_id": "test_edu_003",
        "question": "What is the recommended diagnostic timeline for dengue NS1 antigen test vs IgM?",
        "language": "en",
        "history": [],
        "client_timestamp": None,
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

    final_state = clinical_pipeline.invoke(initial_state)

    assert final_state["route"] == "education"
    assert final_state["evidence_ok"] is True
    assert len(final_state["evidence"]) > 0
    assert final_state["attempts"] == 1
    assert final_state["verdict"] == "pass"
    assert final_state["is_fallback"] is False
    assert len(final_state["answer"]) > 50
    assert "NS1" in final_state["answer"]
    
    # Check trace steps traversed the complete pipeline
    node_names = [t.get("node") for t in final_state["trace_steps"]]
    assert "screener_node" in node_names
    assert "retrieve_node" in node_names
    assert "draft_node" in node_names
    assert "verify_node" in node_names
    assert "publish_node" in node_names

def test_pipeline_out_of_scope_abstain():
    initial_state: DengueGraphState = {
        "session_id": "test_abstain_004",
        "question": "How to repair bicycle chain and paint walls?",
        "language": "en",
        "history": [],
        "client_timestamp": None,
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

    final_state = clinical_pipeline.invoke(initial_state)

    assert final_state["route"] == "uncertain"
    assert final_state["verdict"] == "reject"
    assert final_state["is_fallback"] is True
    assert "consult a certified medical practitioner" in final_state["answer"]
    node_names = [t.get("node") for t in final_state["trace_steps"]]
    assert "screener_node" in node_names
    assert "abstain_node" in node_names
