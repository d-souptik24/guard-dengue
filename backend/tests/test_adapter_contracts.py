"""
GuardDengue — Unit Tests: Canonical Adapter & Data Contracts (Phase 2)

Verifies:
1. CONTRACT_VERSION is "1.0.0" and immutable.
2. TypedDict instantiation and complete JSON-serializability without custom encoders.
3. Correct synthesis of CanonicalEvaluationResult across clinical and medication queries.
4. Schema field completeness across all required evaluation dimensions.
"""
import json
import pytest
from app.retrieval.adapter import (
    CONTRACT_VERSION,
    RequestedScope,
    MedicationAnalysis,
    CanonicalEvaluationResult,
    create_evaluation_adapter,
    create_default_requested_scope,
    get_cached_release_manifest,
)

def test_contract_version_immutability():
    assert CONTRACT_VERSION == "1.0.0"

def test_requested_scope_json_serializable():
    scope: RequestedScope = {
        "jurisdictions": ["India"],
        "jurisdiction_confidence": "explicit",
        "source_authorities_requested": ["NCVBDC"],
        "clinical_topics": ["dengue warning signs"],
        "requires_local_protocol": True,
        "is_emergency_query": False,
    }
    encoded = json.dumps(scope)
    decoded = json.loads(encoded)
    assert decoded["jurisdictions"] == ["India"]
    assert decoded["jurisdiction_confidence"] == "explicit"
    assert decoded["requires_local_protocol"] is True

def test_medication_analysis_json_serializable():
    analysis: MedicationAnalysis = {
        "detected_terms": ["combiflam"],
        "normalization_candidates": ["ibuprofen", "paracetamol"],
        "canonical_ingredients": ["ibuprofen", "paracetamol"],
        "confidence": "high",
        "is_fdc": True,
        "fdc_constituents": ["ibuprofen", "paracetamol"],
        "policy_lookup_statuses": {"ibuprofen": "contraindicated", "paracetamol": "safe"},
        "action_code": "AVOID_FDC_CONTRAINDICATED",
        "template_id": "TMPL_FDC_AVOID_V1",
        "negative_invariants_passed": True,
        "is_chronic_prescription": False,
        "has_negation_cue": False,
    }
    encoded = json.dumps(analysis)
    decoded = json.loads(encoded)
    assert decoded["action_code"] == "AVOID_FDC_CONTRAINDICATED"
    assert decoded["is_fdc"] is True
    assert decoded["negative_invariants_passed"] is True

def test_canonical_evaluation_result_schema_and_serialization():
    scope: RequestedScope = {
        "jurisdictions": ["WHO_GLOBAL"],
        "jurisdiction_confidence": "unknown",
        "source_authorities_requested": ["WHO"],
        "clinical_topics": ["dengue"],
        "requires_local_protocol": False,
        "is_emergency_query": False,
    }
    result: CanonicalEvaluationResult = {
        "contract_version": CONTRACT_VERSION,
        "retrieved_chunk_ids": ["chk-001", "chk-002"],
        "coverage_status": "complete",
        "coverage_reason_codes": [],
        "requested_scope": scope,
        "jurisdiction_coverage": {"requested": "WHO_GLOBAL", "served": "WHO_GLOBAL"},
        "unresolved_required_objects": [],
        "medication_analysis": None,
        "corpus_release": "v0.1-dev",
        "retrieval_mode": "dense",
        "qdrant_collection": "guarddengue_v0.1-dev",
        "release_manifest_hash": "cc71167cc2255d7cd5958d16c76b630ed894af007843f62dc42674ad2eb0a9ed",
        "safety_policy_version": "v0.1-dev",
        "safety_policy_hash": "10bc393f33771f3df1a61a428d4103ca761bebe65b64b8ba80f210a97595df66",
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "latency_ms": 14.25,
    }
    encoded = json.dumps(result)
    decoded = json.loads(encoded)
    assert decoded["contract_version"] == "1.0.0"
    assert len(decoded["retrieved_chunk_ids"]) == 2
    assert decoded["coverage_status"] == "complete"

def test_create_evaluation_adapter_clinical_query():
    query = "What are the warning signs of severe dengue infection?"
    result = create_evaluation_adapter(query, top_k=3)
    
    # Contract invariant checks
    assert result["contract_version"] == "1.0.0"
    assert result["corpus_release"] == "v0.1-dev"
    assert result["retrieval_mode"] == "dense"
    assert len(result["retrieved_chunk_ids"]) > 0
    assert result["coverage_status"] in ["complete", "partial"]
    assert result["latency_ms"] > 0.0
    
    # Metadata assertions
    assert result["release_manifest_hash"] == "cc71167cc2255d7cd5958d16c76b630ed894af007843f62dc42674ad2eb0a9ed"
    assert result["safety_policy_hash"] == "10bc393f33771f3df1a61a428d4103ca761bebe65b64b8ba80f210a97595df66"
    assert result["embedding_model"] == "BAAI/bge-small-en-v1.5"

    # Clinical query should have None medication analysis
    assert result["medication_analysis"] is None

    # Serialization assert
    serialized = json.dumps(result)
    assert len(serialized) > 0

def test_create_evaluation_adapter_medication_query():
    query = "Can I take Combiflam for severe dengue fever?"
    result = create_evaluation_adapter(query, top_k=2)
    
    assert result["contract_version"] == "1.0.0"
    assert result["medication_analysis"] is not None
    assert result["medication_analysis"]["is_fdc"] is True
    assert result["medication_analysis"]["action_code"] == "AVOID_FDC_CONTRAINDICATED"
    assert result["medication_analysis"]["template_id"] == "TMPL_FDC_AVOID_V1"
    assert result["medication_analysis"]["negative_invariants_passed"] is True

def test_create_evaluation_adapter_chronic_prescription_query():
    query = "My cardiologist prescribed daily aspirin for heart stent, should I stop?"
    result = create_evaluation_adapter(query, top_k=2)
    
    assert result["contract_version"] == "1.0.0"
    assert result["medication_analysis"] is not None
    assert result["medication_analysis"]["is_chronic_prescription"] is True
    assert result["medication_analysis"]["action_code"] == "CHRONIC_PRESCRIPTION_ESCALATE"
    assert result["medication_analysis"]["template_id"] == "TMPL_CHRONIC_RX_SAFETY_V1"

def test_cached_release_manifest_singleton():
    manifest1 = get_cached_release_manifest()
    manifest2 = get_cached_release_manifest()
    assert manifest1 is manifest2
    assert manifest1["corpus_release"] == "v0.1-dev"
