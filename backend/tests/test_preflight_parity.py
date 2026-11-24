"""
GuardDengue — Preflight Parity Unit & Fail-Closed Test Suite (Phase 5)

Validates exact parity enforcement and fail-closed behaviors across:
- Successful live parity verification (425 chunks in sync)
- Multi-page scrolling / pagination
- Missing, tampered, or inactive manifests
- Tampered safety policy cryptographic hashes
- SQLite vs Qdrant ID-set mismatches (missing or unexpected points)
- Malformed payloads, null chunk IDs, and duplicate chunk IDs
- Metadata violations (unapproved status, superseded marker, content hash mismatch)
- Quarantine leakage interception
"""

import pytest
import json
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock

from app.core.config import settings
from app.retrieval.vector_store import vector_store
from knowledge_pipeline.preflight import preflight_release_parity_check


def _create_mock_qdrant():
    mock_instance = MagicMock()
    mock_coll = MagicMock()
    mock_coll.name = "guarddengue_v0.1-dev"
    mock_instance.get_collections.return_value.collections = [mock_coll]
    mock_instance.get_aliases.return_value.aliases = []
    return mock_instance


def test_preflight_success_live():
    """Verify live preflight check passes on the active 425-chunk corpus."""
    result = preflight_release_parity_check()
    assert result["status"] == "PASSED"
    assert result["corpus_release"] == "v0.1-dev"
    assert result["approved_chunks_count"] == 425
    assert result["indexed_vectors_count"] == 425
    assert result["unapproved_quarantined_count"] >= 190
    assert result["manifest_sha256"] is not None
    assert result["safety_policy_sha256"] is not None


def test_preflight_pagination_multipage():
    """Verify scroll pagination loops correctly when page limit is smaller than total chunks."""
    result = preflight_release_parity_check(scroll_page_size=50)
    assert result["status"] == "PASSED"
    assert result["indexed_vectors_count"] == 425


def test_preflight_missing_manifest_file():
    """Assert FileNotFoundError if manifest file is missing."""
    with pytest.raises(FileNotFoundError, match="Active release manifest not found"):
        preflight_release_parity_check(manifest_path=Path("non_existent_manifest.json"))


def test_preflight_missing_manifest_field():
    """Assert AssertionError if manifest JSON is missing a required contract field."""
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
        json.dump({"corpus_release": "v0.1-dev", "status": "active"}, tf)
        temp_path = Path(tf.name)

    try:
        with pytest.raises(AssertionError, match="Manifest missing required field"):
            preflight_release_parity_check(manifest_path=temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def test_preflight_inactive_manifest():
    """Assert AssertionError if manifest status is not 'active'."""
    manifest_data = json.loads(
        (settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json").read_text(encoding="utf-8")
    )
    manifest_data["status"] = "deprecated"

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
        json.dump(manifest_data, tf)
        temp_path = Path(tf.name)

    try:
        with pytest.raises(AssertionError, match="Manifest status is not 'active'"):
            preflight_release_parity_check(manifest_path=temp_path)
    finally:
        temp_path.unlink(missing_ok=True)


def test_preflight_policy_hash_mismatch():
    """Assert fail-closed exit if safety policy file hash does not match manifest."""
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
        tf.write('{"tampered": true}')
        temp_policy = Path(tf.name)

    try:
        with pytest.raises(AssertionError, match="Safety policy SHA-256 hash mismatch"):
            preflight_release_parity_check(policy_path=temp_policy)
    finally:
        temp_policy.unlink(missing_ok=True)


def test_preflight_missing_qdrant_collection():
    """Assert AssertionError if target collection or alias does not exist."""
    with pytest.raises(AssertionError, match="Target collection or alias 'non_existent_collection' not found"):
        preflight_release_parity_check(collection_name="non_existent_collection")


def test_preflight_id_set_missing_in_qdrant():
    """Simulate Qdrant missing 1 active chunk -> must fail closed with missing set details."""
    mock_instance = _create_mock_qdrant()

    # Get 424 points from active vector store client
    real_points, _ = vector_store.client.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        limit=424,
        with_payload=True,
        with_vectors=False,
    )
    mock_instance.scroll.return_value = (real_points, None)

    with pytest.raises(AssertionError, match="Indexed vector count mismatch|Qdrant / SQLite ID-set equality violated"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_unexpected_in_qdrant():
    """Simulate Qdrant containing an unapproved or rogue chunk -> must fail closed."""
    mock_instance = _create_mock_qdrant()

    real_points, _ = vector_store.client.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        limit=425,
        with_payload=True,
        with_vectors=False,
    )

    # Add rogue point
    rogue_point = MagicMock()
    rogue_point.id = "rogue-id-123"
    rogue_point.payload = {
        "chunk_id": "rogue-chunk-9999",
        "review_status": "approved",
        "corpus_release": "v0.1-dev",
        "superseded_by": None,
        "chunk_content_hash": "badhash",
    }
    tampered_points = list(real_points) + [rogue_point]
    mock_instance.scroll.return_value = (tampered_points, None)

    with pytest.raises(AssertionError, match="Indexed vector count mismatch|Unexpected in Qdrant"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_quarantine_leak():
    """Simulate a quarantined NCVBDC chunk leaked into Qdrant -> must catch quarantine leakage."""
    mock_instance = _create_mock_qdrant()

    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT chunk_id FROM child_chunks WHERE review_status != 'approved' LIMIT 1")
    quarantined_chunk_id = cur.fetchone()[0]
    conn.close()

    real_points, _ = vector_store.client.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        limit=425,
        with_payload=True,
        with_vectors=False,
    )

    tampered_points = [MagicMock(id=p.id, payload=dict(p.payload)) for p in real_points]
    tampered_points[0].payload["chunk_id"] = quarantined_chunk_id
    mock_instance.scroll.return_value = (tampered_points, None)

    with pytest.raises(AssertionError, match="Quarantine leak detected|Qdrant / SQLite ID-set equality violated"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_payload_review_status_unapproved():
    """Simulate a point with review_status == 'pending_review' -> must fail."""
    mock_instance = _create_mock_qdrant()

    real_points, _ = vector_store.client.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        limit=425,
        with_payload=True,
        with_vectors=False,
    )

    tampered_points = [MagicMock(id=p.id, payload=dict(p.payload)) for p in real_points]
    tampered_points[0].payload["review_status"] = "pending_review"
    mock_instance.scroll.return_value = (tampered_points, None)

    with pytest.raises(AssertionError, match="invalid review_status 'pending_review'"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_payload_superseded_marker():
    """Simulate a point with active superseded_by marker -> must fail."""
    mock_instance = _create_mock_qdrant()

    real_points, _ = vector_store.client.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        limit=425,
        with_payload=True,
        with_vectors=False,
    )

    tampered_points = [MagicMock(id=p.id, payload=dict(p.payload)) for p in real_points]
    tampered_points[0].payload["superseded_by"] = "replacement_chunk_uuid"
    mock_instance.scroll.return_value = (tampered_points, None)

    with pytest.raises(AssertionError, match="active superseded_by marker"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_payload_content_hash_mismatch():
    """Simulate content hash mismatch between Qdrant payload and SQLite -> must fail."""
    mock_instance = _create_mock_qdrant()

    real_points, _ = vector_store.client.scroll(
        collection_name=settings.QDRANT_COLLECTION,
        limit=425,
        with_payload=True,
        with_vectors=False,
    )

    tampered_points = [MagicMock(id=p.id, payload=dict(p.payload)) for p in real_points]
    tampered_points[0].payload["chunk_content_hash"] = "0000000000000000000000000000000000000000000000000000000000000000"
    mock_instance.scroll.return_value = (tampered_points, None)

    with pytest.raises(AssertionError, match="Content hash mismatch for chunk"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_null_chunk_id():
    """Simulate a point with null/missing chunk_id in payload -> must fail closed."""
    mock_instance = _create_mock_qdrant()

    point_no_id = MagicMock()
    point_no_id.id = 1
    point_no_id.payload = {"review_status": "approved"}
    mock_instance.scroll.return_value = ([point_no_id], None)

    with pytest.raises(AssertionError, match="'chunk_id' is null or missing"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_duplicate_chunk_id():
    """Simulate duplicate chunk_id across points -> must fail closed."""
    mock_instance = _create_mock_qdrant()

    point_dup1 = MagicMock()
    point_dup1.id = 1
    point_dup1.payload = {"chunk_id": "same-chunk-id"}
    point_dup2 = MagicMock()
    point_dup2.id = 2
    point_dup2.payload = {"chunk_id": "same-chunk-id"}
    mock_instance.scroll.return_value = ([point_dup1, point_dup2], None)

    with pytest.raises(AssertionError, match="Duplicate chunk_id found in Qdrant"):
        preflight_release_parity_check(client=mock_instance)


def test_preflight_hybrid_success_live():
    """Verify live hybrid preflight confirms non-empty sparse & dense vectors for all 425 chunks."""
    result = preflight_release_parity_check(expected_retrieval_mode="hybrid")
    assert result["status"] == "PASSED"
    assert result["approved_chunks_count"] == 425
    assert result["indexed_vectors_count"] == 425


def test_preflight_hybrid_missing_sparse_vector_config_fails():
    """Hybrid preflight fails closed if collection lacks 'sparse' vector schema."""
    mock_instance = _create_mock_qdrant()
    mock_coll_info = MagicMock()
    mock_coll_info.config.params.sparse_vectors = {}
    mock_instance.get_collection.return_value = mock_coll_info

    with pytest.raises(AssertionError, match="lacks required 'sparse' vector config"):
        preflight_release_parity_check(client=mock_instance, expected_retrieval_mode="hybrid")


def test_preflight_hybrid_empty_sparse_vector_fails():
    """Hybrid preflight fails closed if any Qdrant point has empty sparse indices."""
    mock_instance = _create_mock_qdrant()
    mock_coll_info = MagicMock()
    mock_coll_info.config.params.sparse_vectors = {"sparse": MagicMock()}
    mock_instance.get_collection.return_value = mock_coll_info

    point_empty_sparse = MagicMock()
    point_empty_sparse.id = 1
    point_empty_sparse.payload = {"chunk_id": "chk-empty-sparse", "review_status": "approved"}
    point_empty_sparse.vector = {"dense": [0.1] * 384, "sparse": MagicMock(indices=[])}
    mock_instance.scroll.return_value = ([point_empty_sparse], None)

    with pytest.raises(AssertionError, match="missing non-empty 'dense' or 'sparse' named vector"):
        preflight_release_parity_check(client=mock_instance, expected_retrieval_mode="hybrid")
