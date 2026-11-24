"""
GuardDengue — Hybrid Retrieval & Evidence Synthesis Engine (Zone 4)

Orchestrates semantic search from Qdrant, context enrichment from SQLite parent chunks,
and deterministic semantic coverage evaluation against active guidelines.
Produces validated EvidenceChunk objects conforming to the frontend and evaluation contracts.
"""
from __future__ import annotations

import re
import time
from typing import Any, Literal, overload

from app.core.config import settings
from app.schemas.evidence import EvidenceChunk, EvidenceMetadata
from app.retrieval.vector_store import vector_store
from app.retrieval.sqlite_store import get_parent_chunk
from app.retrieval.adapter import RequestedScope

UNAPPROVED_FIGURE_REFS = {
    "who_dengue_lab_guidance_2025__fig_000",
    "who_dengue_lab_guidance_2025__fig_001",
    "who_dengue_lab_guidance_2025__fig_002",
}


def _enrich_hybrid_clause(clause: str) -> str:
    """Expands unmasked regional NSAID/FDC brand mentions to canonical generic/NSAID terms."""
    from app.safety.drug_registry import analyze_medication_query

    med = analyze_medication_query(clause)
    action = med.get("action_code")
    if action in {"AVOID_NSAID_CONTRAINDICATED", "AVOID_FDC_CONTRAINDICATED", "CHRONIC_PRESCRIPTION_ESCALATE"}:
        q_lower = clause.lower()
        ingredients = [
            ing.replace("_", " ")
            for ing in (med.get("canonical_ingredients") or [])
            if ing != "paracetamol"
        ]
        missing_canon = [ing for ing in ingredients if ing not in q_lower]
        if missing_canon and "nsaid" not in q_lower and "non-steroidal" not in q_lower:
            return f"{clause} non-steroidal anti-inflammatory medications NSAIDs {' '.join(missing_canon)}".strip()
    return clause

class RetrievalEngine:
    def __init__(self):
        self.vector_store = vector_store
        self.last_reason_codes: list[str] = []
        self.last_requested_scope: RequestedScope | None = None

    def _determine_requested_scope(self, query: str) -> RequestedScope:
        """
        Analyzes the query for geographical jurisdiction, local protocol requirements,
        and emergency warning sign indicators.
        """
        clean_q = query.lower()

        # Explicit Indian geography & authority indicators
        explicit_india_terms = [
            "india", "indian", "west bengal", "kolkata", "delhi", "nvbdcp",
            "ncvbdc", "asha", "phc", "chc", "aiims", "national guideline", "national protocol"
        ]
        has_explicit_india = any(
            re.search(rf"\b{re.escape(term)}\b", clean_q) for term in explicit_india_terms
        )

        # Explicit WHO / Global indicators
        explicit_who_terms = ["who", "world health organization", "global guideline", "international"]
        has_explicit_who = any(
            re.search(rf"\b{re.escape(term)}\b", clean_q) for term in explicit_who_terms
        )

        # Red-flag emergency symptoms (Decoupled from audit completeness)
        emergency_patterns = [
            r"\bshock\b",
            r"\bsevere\s+abdominal\s+pain\b",
            r"\bpersistent\s+vomiting\b",
            r"\bmucosal\s+bleeding\b",
            r"\bbleeding\s+(gums?|nose|mouth)\b",
            r"\bcold\s+clammy\b",
            r"\bfluid\s+accumulation\b",
            r"\bplasma\s+leakage\b",
            r"\b(dss|dengue\s+shock)\b",
            r"\bvomiting\s+blood\b",
            r"\bblack\s+stools?\b",
            r"\blethargy\b",
            r"\brestlessness\b"
        ]
        is_emergency = any(re.search(pat, clean_q) for pat in emergency_patterns)

        if has_explicit_india:
            jurisdictions = ["India"]
            confidence: Literal["explicit", "inferred", "unknown"] = "explicit"
            authorities = ["NCVBDC"]
            requires_local = True
        elif has_explicit_who:
            jurisdictions = ["WHO_GLOBAL"]
            confidence = "explicit"
            authorities = ["WHO"]
            requires_local = False
        else:
            jurisdictions = ["WHO_GLOBAL"]
            confidence = "unknown"
            authorities = ["WHO"]
            requires_local = False

        return {
            "jurisdictions": jurisdictions,
            "jurisdiction_confidence": confidence,
            "source_authorities_requested": authorities,
            "clinical_topics": ["dengue"],
            "requires_local_protocol": requires_local,
            "is_emergency_query": is_emergency,
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        topic: str | None = None,
        return_details: bool = False,
        score_threshold: float = 0.60,
        retrieval_mode: Literal["dense", "hybrid"] | None = None,
        prefetch_limit: int | None = None,
        collection_name: str | None = None,
        dense_oos_floor: float | None = None,
    ) -> tuple[Any, ...]:
        """
        Retrieves grounded clinical evidence chunks and computes semantic coverage status.
        
        Args:
            query: Citizen or clinician search query.
            top_k: Number of candidate chunks to retrieve.
            topic: Optional taxonomy filter.
            return_details: If True, returns full 6-tuple with coverage reason codes and requested scope.
                            If False (default), returns canonical 4-tuple for LangGraph pipeline compatibility.
            score_threshold: Minimum cosine similarity floor (0.60 for clinical relevancy vs out-of-scope).
            retrieval_mode: Optional override ('dense' or 'hybrid'). Defaults to settings.RETRIEVAL_MODE.
            prefetch_limit: Optional hybrid prefetch limit override.
            collection_name: Optional Qdrant collection override.
            dense_oos_floor: Optional OOS dense cosine floor in hybrid mode.
        """
        start_time = time.perf_counter()
        clean_q = query.lower()
        requested_scope = self._determine_requested_scope(query)
        active_mode = retrieval_mode or getattr(settings, "RETRIEVAL_MODE", "dense")

        search_query = _enrich_hybrid_clause(query) if active_mode == "hybrid" else query
        raw_hits = self.vector_store.search(
            query=search_query,
            top_k=top_k,
            topic=topic,
            score_threshold=score_threshold,
            retrieval_mode=retrieval_mode,
            prefetch_limit=prefetch_limit,
            collection_name=collection_name,
            dense_oos_floor=dense_oos_floor,
        )
        
        evidence_chunks: list[EvidenceChunk] = []
        for hit in raw_hits:
            payload = hit.get("payload", {})
            chunk_id = payload.get("chunk_id", f"CHK-{hit['id']}")
            parent_id = payload.get("parent_id")
            
            # Skip redundant synchronous SQLite parent queries when section_path is already populated in payload
            parent_info = get_parent_chunk(parent_id) if (parent_id and not payload.get("section_path")) else None
            
            topics = payload.get("topic", ["Dengue basics"])
            if isinstance(topics, list) and len(topics) > 0:
                primary_category = topics[0]
            elif isinstance(topics, str):
                primary_category = topics
            else:
                primary_category = "Dengue basics"

            metadata = EvidenceMetadata(
                source=payload.get("source", "WHO Clinical Management Guidelines 2024"),
                publication_date=payload.get("publication_date", "2024-08-10"),
                evidence_level=payload.get("evidence_level", "Level 1 (Global Clinical Practice Guideline)"),
                topic=topics,
                chunk_id=chunk_id,
                review_status=payload.get("review_status", "approved"),
                corpus_release=payload.get("corpus_release", settings.CORPUS_RELEASE),
                section_path=payload.get("section_path", parent_info.get("section_path") if parent_info else None),
                page_start=payload.get("page_start"),
                page_end=payload.get("page_end")
            )

            evidence_chunks.append(
                EvidenceChunk(
                    id=chunk_id,
                    score=round(hit.get("score", 1.0), 4),
                    category=primary_category,
                    content=payload.get("text", ""),
                    metadata=metadata
                )
            )

        # ─── Deterministic Semantic Coverage Decision Matrix ─────────────────────
        has_explicit_ncvbdc_demand = any(
            t in clean_q for t in ["ncvbdc", "nvbdcp", "national guideline", "national guidelines", "national protocol"]
        )

        is_figure_query = any(
            t in clean_q for t in ["fig_000", "fig_001", "fig_002", "figure 1", "figure 2", "diagnostic algorithm flowchart", "laboratory flowchart"]
        )
        has_pending_figure_chunk = any(
            any(ref in (chunk.content or "") for ref in UNAPPROVED_FIGURE_REFS)
            for chunk in evidence_chunks
        )

        reason_codes: list[str] = []
        coverage_status: Literal["complete", "partial", "unavailable"]
        evidence_ok: bool

        if len(evidence_chunks) == 0:
            evidence_ok = False
            coverage_status = "unavailable"
            if has_explicit_ncvbdc_demand or requested_scope["requires_local_protocol"]:
                reason_codes = ["EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE"]
            else:
                reason_codes = ["NO_APPROVED_EVIDENCE"]
        elif has_explicit_ncvbdc_demand:
            # Explicit national protocol requested, but NCVBDC is quarantined; only global WHO returned
            coverage_status = "unavailable"
            reason_codes = ["EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE"]
            evidence_ok = False
        else:
            evidence_ok = True
            
            # Check unreviewed figure artifacts
            if is_figure_query or has_pending_figure_chunk:
                coverage_status = "partial"
                reason_codes.append("FIGURE_PENDING_REVIEW")

            # Check jurisdiction coverage
            if requested_scope["requires_local_protocol"]:
                coverage_status = "partial"
                if "LOCAL_PROTOCOL_UNAVAILABLE_GLOBAL_SUBSTITUTED" not in reason_codes:
                    reason_codes.append("LOCAL_PROTOCOL_UNAVAILABLE_GLOBAL_SUBSTITUTED")
            elif requested_scope["jurisdiction_confidence"] == "unknown":
                coverage_status = "partial"
                if "JURISDICTION_UNCONFIRMED" not in reason_codes:
                    reason_codes.append("JURISDICTION_UNCONFIRMED")
            elif not reason_codes:
                coverage_status = "complete"

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        self.last_reason_codes = reason_codes
        self.last_requested_scope = requested_scope

        if return_details:
            return evidence_chunks, evidence_ok, coverage_status, reason_codes, requested_scope, round(latency_ms, 2)
        return evidence_chunks, evidence_ok, coverage_status, round(latency_ms, 2)

# Singleton instance
retrieval_engine = RetrievalEngine()
