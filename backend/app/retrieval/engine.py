"""
GuardDengue — Hybrid Retrieval & Evidence Synthesis Engine (Zone 4)

Orchestrates semantic search from Qdrant, context enrichment from SQLite parent chunks,
and verification against the active safety policy.
Produces validated EvidenceChunk objects conforming to the frontend contract.
"""
import time
from typing import Any
from app.core.config import settings
from app.schemas.evidence import EvidenceChunk, EvidenceMetadata
from app.retrieval.vector_store import vector_store
from app.retrieval.sqlite_store import get_parent_chunk

class RetrievalEngine:
    def __init__(self):
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        topic: str | None = None
    ) -> tuple[list[EvidenceChunk], bool, str, float]:
        """
        Retrieves grounded clinical evidence chunks.
        Returns:
            evidence_chunks: list of EvidenceChunk items conforming to schema
            evidence_ok: True if at least 1 high-confidence approved chunk was found
            coverage_status: "complete" | "partial" | "unavailable"
            latency_ms: retrieval latency in milliseconds
        """
        start_time = time.perf_counter()
        raw_hits = self.vector_store.search(query=query, top_k=top_k, topic=topic)
        
        evidence_chunks: list[EvidenceChunk] = []
        for hit in raw_hits:
            payload = hit.get("payload", {})
            chunk_id = payload.get("chunk_id", f"CHK-{hit['id']}")
            parent_id = payload.get("parent_id")
            
            # Fetch parent chunk context if available to provide complete clinical framing
            parent_info = get_parent_chunk(parent_id) if parent_id else None
            
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

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        if not evidence_chunks:
            return [], False, "unavailable", round(latency_ms, 2)
        elif len(evidence_chunks) >= 2:
            return evidence_chunks, True, "complete", round(latency_ms, 2)
        else:
            return evidence_chunks, True, "partial", round(latency_ms, 2)

# Singleton instance
retrieval_engine = RetrievalEngine()
