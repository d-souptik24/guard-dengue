"""
GuardDengue — Unit Tests: Zone 4 Retrieval & Storage Adapters

Tests:
1. SQLite store queries for parent chunks and active corpus release.
2. Local safety policy lookup and contraindication checks.
3. Qdrant vector retrieval with metadata filtering.
4. RetrievalEngine evidence synthesis.
"""
import pytest
from app.retrieval.sqlite_store import get_parent_chunk, get_child_chunk, get_active_corpus_release
from app.retrieval.policy_store import policy_store
from app.retrieval.vector_store import vector_store
from app.retrieval.engine import retrieval_engine

def test_sqlite_parent_chunk_fetch():
    parent = get_parent_chunk("44f01082-d4be-52f9-83bf-a1b92fef081b")
    assert parent is not None
    assert parent["doc_id"] == "who_dengue_lab_guidance_2025"
    assert len(parent["text"]) > 0

def test_sqlite_child_chunk_fetch():
    child = get_child_chunk("1c26a00f-7a98-5746-897b-6da689d4ddd1")
    assert child is not None
    assert child["parent_id"] == "44f01082-d4be-52f9-83bf-a1b92fef081b"
    assert child["review_status"] == "approved"

def test_active_corpus_release():
    release = get_active_corpus_release()
    assert release == "v0.1-dev"

def test_policy_store_nsaid_check():
    rule = policy_store.is_contraindicated("combiflam")
    assert rule is not None
    assert rule["action"] == "AVOID_IN"
    assert "Paracetamol" in rule["safe_alternatives"]

def test_policy_store_paracetamol_not_contraindicated():
    rule = policy_store.is_contraindicated("paracetamol")
    assert rule is None

def test_vector_store_search():
    hits = vector_store.search("What are the warning signs of severe dengue?", top_k=3)
    assert len(hits) > 0
    first_hit = hits[0]
    assert "payload" in first_hit
    assert first_hit["payload"]["review_status"] == "approved"
    assert "chunk_id" in first_hit["payload"]

def test_retrieval_engine_synthesis():
    chunks, ok, coverage, latency = retrieval_engine.retrieve("When should dengue NS1 antigen test be done?")
    assert ok is True
    assert coverage in ["complete", "partial"]
    assert len(chunks) > 0
    first_chunk = chunks[0]
    # Verify strict 4-field metadata contract
    assert first_chunk.metadata.source is not None
    assert first_chunk.metadata.publication_date is not None
    assert first_chunk.metadata.evidence_level is not None
    assert first_chunk.metadata.topic is not None
    assert latency >= 0.0
