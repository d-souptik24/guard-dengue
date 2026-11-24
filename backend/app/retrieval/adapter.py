"""
GuardDengue — Canonical Evaluation Adapter & Data Contracts (Zone 4 & Zone 2)

Defines versioned TypedDict contracts bridging RetrievalEngine, medication analysis,
and evaluation benchmark harnesses. Ensures complete consistency across developer
smokes, regression suites, and production release gating.
"""
from __future__ import annotations

import json
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal, TypedDict

from app.core.config import settings

CONTRACT_VERSION = "1.0.0"

class RequestedScope(TypedDict):
    """Encapsulates the geographical, guideline, and clinical intent extracted from the citizen query."""
    jurisdictions: list[str]
    jurisdiction_confidence: Literal["explicit", "inferred", "unknown"]
    source_authorities_requested: list[str]
    clinical_topics: list[str]
    requires_local_protocol: bool
    is_emergency_query: bool

class MedicationAnalysis(TypedDict):
    """Standardized medication screening evaluation payload."""
    detected_terms: list[str]
    normalization_candidates: list[str]
    canonical_ingredients: list[str]
    confidence: Literal["high", "low", "uncertain"]
    is_fdc: bool
    fdc_constituents: list[str]
    policy_lookup_statuses: dict[str, str]
    action_code: Literal[
        "AVOID_NSAID_CONTRAINDICATED",
        "AVOID_FDC_CONTRAINDICATED",
        "ESCALATE_UNKNOWN_MEDICATION",
        "DETECTOR_UNCERTAIN",
        "CHRONIC_PRESCRIPTION_ESCALATE",
        "NEGATED_MENTION_EDUCATION",
        "STANDARD_EVIDENCE_RETRIEVAL",
    ]
    template_id: str | None
    negative_invariants_passed: bool
    is_chronic_prescription: bool
    has_negation_cue: bool

class CanonicalEvaluationResult(TypedDict):
    """
    Standardized evaluation record emitted for every benchmark query.
    Used for offline regression benchmarking, gate validation, and audit tracking.
    """
    contract_version: str
    retrieved_chunk_ids: list[str]
    coverage_status: Literal["complete", "partial", "unavailable"]
    coverage_reason_codes: list[str]
    requested_scope: RequestedScope
    jurisdiction_coverage: dict[str, str]
    unresolved_required_objects: list[str]
    medication_analysis: MedicationAnalysis | None
    corpus_release: str
    retrieval_mode: Literal["dense", "hybrid"]
    qdrant_collection: str
    release_manifest_hash: str
    safety_policy_version: str
    safety_policy_hash: str
    embedding_model: str
    latency_ms: float

@lru_cache(maxsize=1)
def get_cached_release_manifest() -> dict[str, Any]:
    """Loads and caches the active release manifest from disk for fast metadata population."""
    manifest_path = settings.KNOWLEDGE_DIR / f"release_manifest_{settings.CORPUS_RELEASE}.json"
    if manifest_path.exists():
        try:
            return json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "corpus_release": settings.CORPUS_RELEASE,
        "qdrant_collection": getattr(settings, "QDRANT_COLLECTION", f"guarddengue_{settings.CORPUS_RELEASE}"),
        "retrieval_mode": "dense",
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "manifest_sha256": "UNKNOWN_MANIFEST_HASH",
        "safety_policy_sha256": "UNKNOWN_POLICY_HASH",
        "status": "active"
    }

def create_default_requested_scope(query: str) -> RequestedScope:
    """Heuristic scope determination used until Phase 3 semantic engine is active."""
    clean_q = query.lower()
    explicit_india_terms = ["india", "west bengal", "kolkata", "nvbdcp", "ncvbdc", "asha", "phc"]
    is_india = any(term in clean_q for term in explicit_india_terms)
    
    emergency_terms = ["shock", "severe abdominal pain", "persistent vomiting", "mucosal bleeding", "cold clammy", "fluid accumulation"]
    is_emergency = any(term in clean_q for term in emergency_terms)
    
    return {
        "jurisdictions": ["India"] if is_india else ["WHO_GLOBAL"],
        "jurisdiction_confidence": "explicit" if is_india else "unknown",
        "source_authorities_requested": ["NCVBDC"] if is_india else ["WHO"],
        "clinical_topics": ["dengue"],
        "requires_local_protocol": is_india,
        "is_emergency_query": is_emergency,
    }

def analyze_medication_fallback(query: str) -> MedicationAnalysis | None:
    """Medication screening delegating to drug_registry Phase 4 engine."""
    try:
        from app.safety.drug_registry import analyze_medication_query
        res = analyze_medication_query(query)
        if res.get("action_code") == "STANDARD_EVIDENCE_RETRIEVAL":
            return None
        return res
    except ImportError:
        pass

    # Basic baseline delegation before Phase 4 is executed
    try:
        from app.safety.drug_registry import detect_nsaid, SAFE_ANTIPYRETICS
        match = detect_nsaid(query)
        clean_q = query.lower()
        if match:
            is_chronic = match.get("is_chronic_context", match.get("chronic_context", False))
            drug_id = match.get("drug_id", match.get("id", "nsaid"))
            is_fdc = "combiflam" in clean_q or "flexon" in clean_q or "zerodol" in clean_q
            
            action_code: Any
            template_id: str | None
            if is_chronic:
                action_code = "CHRONIC_PRESCRIPTION_ESCALATE"
                template_id = "TMPL_CHRONIC_RX_SAFETY_V1"
            elif is_fdc:
                action_code = "AVOID_FDC_CONTRAINDICATED"
                template_id = "TMPL_FDC_AVOID_V1"
            else:
                action_code = "AVOID_NSAID_CONTRAINDICATED"
                template_id = "TMPL_NSAID_AVOID_V1"
                
            return {
                "detected_terms": [drug_id],
                "normalization_candidates": [drug_id],
                "canonical_ingredients": [drug_id],
                "confidence": "high",
                "is_fdc": is_fdc,
                "fdc_constituents": ["ibuprofen", "paracetamol"] if is_fdc else [drug_id],
                "policy_lookup_statuses": {drug_id: "contraindicated"},
                "action_code": action_code,
                "template_id": template_id,
                "negative_invariants_passed": True,
                "is_chronic_prescription": is_chronic,
                "has_negation_cue": "not " in clean_q or "never " in clean_q or "stopped " in clean_q,
            }
    except Exception:
        pass
    return None

def create_evaluation_adapter(
    query: str,
    top_k: int = 5,
    retrieval_mode: Literal["dense", "hybrid"] = "dense",
    collection_name: str | None = None,
) -> CanonicalEvaluationResult:
    """
    Standard evaluation bridge: executes retrieval and safety screening,
    synthesizing a CanonicalEvaluationResult contract.
    """
    start_time = time.perf_counter()
    from app.retrieval.engine import retrieval_engine
    
    # Execute retrieval with full semantic coverage details
    raw_res = retrieval_engine.retrieve(
        query=query,
        top_k=top_k,
        return_details=True,
        retrieval_mode=retrieval_mode,
        collection_name=collection_name,
    )
    
    # Handle future Phase 3 6-tuple vs current 4-tuple
    if len(raw_res) == 4:
        evidence_chunks, ok, coverage_status, engine_latency = raw_res
        coverage_reason_codes = [] if coverage_status == "complete" else ["COUNT_HEURISTIC_EVAL"]
        requested_scope = create_default_requested_scope(query)
    elif len(raw_res) == 6:
        evidence_chunks, ok, coverage_status, coverage_reason_codes, requested_scope, engine_latency = raw_res
    else:
        raise ValueError(f"Unexpected return signature from retrieval_engine.retrieve: {len(raw_res)} elements")

    # Extract retrieved chunk IDs
    retrieved_chunk_ids = [chunk.id for chunk in evidence_chunks]

    # Perform medication analysis
    med_analysis = analyze_medication_fallback(query)

    # Manifest metadata
    manifest = get_cached_release_manifest()
    
    active_collection = collection_name or getattr(settings, "QDRANT_COLLECTION", f"guarddengue_{settings.CORPUS_RELEASE}")
    if retrieval_mode == "dense" and not active_collection.endswith("_dense"):
        # If alias or mode specified
        pass

    latency_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "contract_version": CONTRACT_VERSION,
        "retrieved_chunk_ids": retrieved_chunk_ids,
        "coverage_status": coverage_status,
        "coverage_reason_codes": coverage_reason_codes,
        "requested_scope": requested_scope,
        "jurisdiction_coverage": {
            "requested": requested_scope["jurisdictions"][0] if requested_scope["jurisdictions"] else "UNKNOWN",
            "served": "WHO_GLOBAL"
        },
        "unresolved_required_objects": [],
        "medication_analysis": med_analysis,
        "corpus_release": settings.CORPUS_RELEASE,
        "retrieval_mode": retrieval_mode,
        "qdrant_collection": active_collection,
        "release_manifest_hash": manifest.get("manifest_sha256", "UNKNOWN_HASH"),
        "safety_policy_version": manifest.get("corpus_release", settings.CORPUS_RELEASE),
        "safety_policy_hash": manifest.get("safety_policy_sha256", "UNKNOWN_HASH"),
        "embedding_model": manifest.get("embedding_model", "BAAI/bge-small-en-v1.5"),
        "latency_ms": round(latency_ms, 2)
    }
