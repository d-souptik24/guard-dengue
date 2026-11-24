"""
GuardDengue — Unit & Integration Tests: Phase 8A Hybrid BM25 + Dense RRF Retrieval

Covers:
1. Fail-closed Qdrant/bm25 behavior when USE_FASTEMBED != "1" (no MD5 fallback).
2. Deterministic BM25 sparse vector generation shape and types.
3. Lexical-mismatch retrieval rescue via hybrid RRF (EDTA specimen tube) and Zone 2->4
   regional brand normalization (Brufen -> NSAID guideline).
4. Rank 2-5 RRF survival (scores below 0.60 preserved when candidate dense cosine >= floor).
5. Out-of-scope domain abstention gate under hybrid mode (both RetrievalEngine and LangGraph).
6. Adapter retrieval_mode propagation ("dense" vs "hybrid") and contract version parity.
7. Benchmark validator pass confirmation for Calibration (35) and Held-Out Validation (50) splits.
"""
from __future__ import annotations

import pytest

from app.core.config import settings
from app.graph.workflow import clinical_pipeline
from app.retrieval import embeddings as emb_mod
from app.retrieval.adapter import CONTRACT_VERSION, create_evaluation_adapter
from app.retrieval.engine import retrieval_engine
from app.retrieval.vector_store import vector_store
from knowledge_pipeline.validate_benchmark import validate_benchmark


def test_sparse_bm25_fails_closed_when_fastembed_disabled(monkeypatch: pytest.MonkeyPatch):
    """Hybrid sparse embeddings must raise RuntimeError rather than falling back to MD5."""
    monkeypatch.setattr(emb_mod, "_SPARSE_BM25_MODEL", None)
    monkeypatch.setenv("USE_FASTEMBED", "0")

    with pytest.raises(RuntimeError, match="failed closed"):
        emb_mod.get_sparse_bm25_embedding("dengue fever EDTA tube", is_query=True)


def test_sparse_bm25_vector_shape():
    """Validates non-empty integer indices and float TF/IDF weights from Qdrant/bm25."""
    vec = emb_mod.get_sparse_bm25_embedding("ethylenediaminetetraacetic acid EDTA whole blood", is_query=True)
    assert isinstance(vec, dict)
    assert "indices" in vec and "values" in vec
    assert len(vec["indices"]) > 0
    assert len(vec["indices"]) == len(vec["values"])
    assert all(isinstance(i, int) for i in vec["indices"])
    assert all(isinstance(v, (int, float)) for v in vec["values"])


def test_hybrid_rrf_lexical_mismatch_edta_and_brufen():
    """Hybrid RRF rescues lexical acronym (EDTA) and Zone 2-normalized brand (Brufen -> NSAID)."""
    edta_chunks, edta_ok, _, _, _, _ = retrieval_engine.retrieve(
        "What blood sample tube is recommended for RT-PCR detection of dengue virus?",
        top_k=5,
        return_details=True,
        retrieval_mode="hybrid",
    )
    assert edta_ok is True
    assert any("edta" in chunk.content.lower() for chunk in edta_chunks)

    brufen_chunks, brufen_ok, _, _, _, _ = retrieval_engine.retrieve(
        "Can I take Brufen tablet for fever and body pain in suspected dengue?",
        top_k=5,
        return_details=True,
        retrieval_mode="hybrid",
    )
    assert brufen_ok is True
    assert any(
        "non-steroidal anti-inflammatory" in chunk.content.lower() or "nsaid" in chunk.content.lower()
        for chunk in brufen_chunks
    )


def test_hybrid_rrf_rank2_to_5_survival():
    """Rank 2-5 RRF scores (< 0.60) must survive when candidate dense cosine clears OOS floor."""
    hits = vector_store.search(
        query="When should dengue NS1 antigen test be done?",
        top_k=5,
        retrieval_mode="hybrid",
        prefetch_limit=20,
        dense_oos_floor=settings.HYBRID_DENSE_OOS_FLOOR,
    )
    assert len(hits) == 5
    # Verify Qdrant RRF Rank 2..5 produce sub-0.60 fusion scores yet are NOT pruned
    assert any(h["score"] < 0.60 for h in hits[1:])


@pytest.mark.parametrize(
    "oos_query",
    [
        "How do I replace a worn bicycle chain and tune derailleur gears?",
        "What SQL query optimizes B-tree index scans in PostgreSQL tables?",
    ],
)
def test_hybrid_out_of_scope_abstain(monkeypatch: pytest.MonkeyPatch, oos_query: str):
    """Out-of-scope and stopword-colliding queries abstain cleanly via NO_APPROVED_EVIDENCE."""
    monkeypatch.setattr(settings, "RETRIEVAL_MODE", "hybrid")

    chunks, ok, coverage, reason_codes, _, _ = retrieval_engine.retrieve(
        oos_query,
        top_k=5,
        return_details=True,
        retrieval_mode="hybrid",
    )
    assert chunks == []
    assert ok is False
    assert coverage == "unavailable"
    assert "NO_APPROVED_EVIDENCE" in reason_codes

    adapter_out = create_evaluation_adapter(query=oos_query, top_k=5, retrieval_mode="hybrid")
    assert adapter_out["retrieved_chunk_ids"] == []
    assert adapter_out["coverage_status"] == "unavailable"
    assert "NO_APPROVED_EVIDENCE" in adapter_out["coverage_reason_codes"]

    graph_out = clinical_pipeline.invoke(
        {
            "session_id": "test-hybrid-oos",
            "question": oos_query,
            "language": "en",
            "history": [],
        }
    )
    assert graph_out.get("evidence", []) == []
    assert graph_out.get("verdict") != "pass"


def test_adapter_retrieval_mode_parity():
    """Canonical adapter surfaces retrieval_mode accurately while preserving contract invariants."""
    q = "When is capillary refill time considered abnormal in severe dengue?"
    dense_res = create_evaluation_adapter(query=q, top_k=5, retrieval_mode="dense")
    hybrid_res = create_evaluation_adapter(query=q, top_k=5, retrieval_mode="hybrid")

    assert dense_res["contract_version"] == CONTRACT_VERSION
    assert hybrid_res["contract_version"] == CONTRACT_VERSION
    assert dense_res["retrieval_mode"] == "dense"
    assert hybrid_res["retrieval_mode"] == "hybrid"
    assert dense_res["qdrant_collection"] == hybrid_res["qdrant_collection"]
    assert len(dense_res["retrieved_chunk_ids"]) > 0
    assert len(hybrid_res["retrieved_chunk_ids"]) > 0


def test_phase8a_benchmarks_validate_cleanly():
    """Both Calibration (35) and Held-Out Validation (50) JSONLs resolve 100% against SQLite."""
    calib = validate_benchmark(settings.KNOWLEDGE_DIR / "eval_dev_calib.jsonl")
    assert calib["status"] == "PASSED"
    assert calib["total_cases"] == 35
    assert calib["failure_count"] == 0

    val = validate_benchmark(settings.KNOWLEDGE_DIR / "eval_dev_validation.jsonl")
    assert val["status"] == "PASSED"
    assert val["total_cases"] == 50
    assert val["failure_count"] == 0

