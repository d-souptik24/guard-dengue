"""
GuardDengue — Unit Tests: Semantic Coverage Engine & Decision Matrix (Phase 3)

Validates the 6 canonical rows of the Semantic Coverage Decision Matrix:
1. Row 1: Standard Approved Query (Explicit WHO / Global) -> complete, []
2. Row 2: Explicit Indian Protocol (NCVBDC quarantined) -> unavailable, ["EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE"]
3. Row 3: General India Query (WHO evidence substituted) -> partial, ["LOCAL_PROTOCOL_UNAVAILABLE_GLOBAL_SUBSTITUTED"]
4. Row 4: Unconfirmed Jurisdiction -> partial, ["JURISDICTION_UNCONFIRMED"]
5. Row 5: Pending Figure Reference -> partial, ["FIGURE_PENDING_REVIEW"]
6. Row 6: Red-Flag Emergency Query -> is_emergency_query = True (Decoupled urgency)
7. Zero Results Fallback -> unavailable, ["NO_APPROVED_EVIDENCE"]
"""
import pytest
from app.retrieval.engine import retrieval_engine

def test_row1_standard_approved_query_complete():
    """Row 1: Explicit WHO global question with approved chunks -> complete, reason_codes: []"""
    query = "According to WHO guidelines, what is the recommended diagnostic timeline for dengue NS1 antigen test vs IgM?"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    assert ok is True
    assert len(chunks) > 0
    assert scope["jurisdictions"] == ["WHO_GLOBAL"]
    assert scope["jurisdiction_confidence"] == "explicit"
    assert coverage_status == "complete"
    assert reason_codes == []

def test_row2_explicit_ncvbdc_protocol_unavailable():
    """Row 2: Explicit demand for quarantined Indian national protocol -> unavailable"""
    query = "What is the official NCVBDC national guideline recommendation for primary health centers in India?"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    assert ok is False
    assert coverage_status == "unavailable"
    assert "EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE" in reason_codes
    assert scope["requires_local_protocol"] is True

def test_row3_general_india_query_who_substituted():
    """Row 3: General Indian context with WHO evidence substituted -> partial, LOCAL_PROTOCOL_UNAVAILABLE_GLOBAL_SUBSTITUTED"""
    query = "What are the recommended platelet thresholds for platelet transfusion in West Bengal dengue patients?"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    assert ok is True
    assert len(chunks) > 0
    assert scope["jurisdictions"] == ["India"]
    assert scope["requires_local_protocol"] is True
    assert coverage_status == "partial"
    assert "LOCAL_PROTOCOL_UNAVAILABLE_GLOBAL_SUBSTITUTED" in reason_codes

def test_row4_unconfirmed_jurisdiction():
    """Row 4: Clinical query without geographical anchor -> partial, JURISDICTION_UNCONFIRMED"""
    query = "What are the primary clinical warning signs of severe plasma leakage in dengue?"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    assert ok is True
    assert len(chunks) > 0
    assert scope["jurisdiction_confidence"] == "unknown"
    assert coverage_status == "partial"
    assert "JURISDICTION_UNCONFIRMED" in reason_codes

def test_row5_pending_figure_reference():
    """Row 5: Query referencing unreviewed figure artifact -> partial, FIGURE_PENDING_REVIEW"""
    query = "Explain the algorithm in who_dengue_lab_guidance_2025__fig_001 for laboratory diagnostic flowchart"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    assert coverage_status == "partial"
    assert "FIGURE_PENDING_REVIEW" in reason_codes

def test_row6_emergency_query_decoupling():
    """Row 6: Red-flag emergency query sets is_emergency_query without breaking evidence coverage"""
    query = "Patient has dengue shock syndrome, cold clammy extremities, and severe abdominal pain"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    # Decoupled emergency detection invariant
    assert scope["is_emergency_query"] is True
    assert coverage_status in ["complete", "partial", "unavailable"]

def test_zero_results_no_approved_evidence():
    """Zero chunks returned for non-existent topic -> unavailable, NO_APPROVED_EVIDENCE"""
    query = "Quantum entanglement superconductors in semiconductor manufacturing zyxwv987"
    chunks, ok, coverage_status, reason_codes, scope, latency = retrieval_engine.retrieve(query, top_k=3, return_details=True)
    
    assert ok is False
    assert len(chunks) == 0
    assert coverage_status == "unavailable"
    assert "NO_APPROVED_EVIDENCE" in reason_codes

def test_backward_compatible_4_tuple_return():
    """Verifies that retrieve(..., return_details=False) returns canonical 4-tuple for LangGraph"""
    res = retrieval_engine.retrieve("When should dengue NS1 antigen test be done?", top_k=2)
    assert len(res) == 4
    chunks, ok, coverage_status, latency = res
    assert isinstance(chunks, list)
    assert isinstance(ok, bool)
    assert isinstance(coverage_status, str)
    assert isinstance(latency, float)
