"""
GuardDengue — Paginated Preflight Parity Suite (Phase 5)

Enforces exact cryptographic, relational, and vector synchronization across:
1. Active release manifest (release_manifest_v0.1-dev.json)
2. Safety policy (safety_policy_v0.1-dev.json)
3. SQLite chunk repository (guarddengue_chunks.db)
4. Local Qdrant vector index (guarddengue_v0.1-dev / guarddengue_v0.1-dev_dense)

Any mismatch, missing point, stale vector, or quarantine leak fails closed immediately.
"""

from pathlib import Path
import json
import hashlib
import sqlite3
import sys
import argparse
from typing import Dict, Any, Optional
from qdrant_client import QdrantClient

# Support standalone CLI execution as well as internal imports
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings


def preflight_release_parity_check(
    manifest_path: Optional[Path | str] = None,
    db_path: Optional[Path | str] = None,
    qdrant_path: Optional[Path | str] = None,
    policy_path: Optional[Path | str] = None,
    collection_name: Optional[str] = None,
    scroll_page_size: int = 100,
    client: Optional[QdrantClient] = None,
    expected_retrieval_mode: str = "dense",
) -> Dict[str, Any]:
    """
    Executes a comprehensive, fail-closed preflight parity audit.
    Validates manifest hashes, SQLite table consistency, and paginated Qdrant index.
    """
    # 1. Resolve & validate manifest on disk
    if manifest_path is None:
        candidates = [
            settings.KNOWLEDGE_DIR / f"release_manifest_{settings.CORPUS_RELEASE}.json",
            settings.DATA_DIR / f"release_manifest_{settings.CORPUS_RELEASE}.json",
        ]
        manifest_path = next((p for p in candidates if p.exists()), candidates[0])
    
    manifest_path = Path(manifest_path)
    if not manifest_path.exists():
        raise FileNotFoundError(f"Active release manifest not found at {manifest_path}")

    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as e:
        raise ValueError(f"Failed to parse release manifest JSON at {manifest_path}: {e}")

    required_manifest_fields = [
        "corpus_release",
        "qdrant_collection",
        "retrieval_mode",
        "embedding_model",
        "manifest_sha256",
        "safety_policy_sha256",
        "approved_chunks",
        "indexed_vectors",
        "status",
    ]
    for field in required_manifest_fields:
        if field not in manifest_data:
            raise AssertionError(f"Manifest missing required field: '{field}'")

    if manifest_data.get("status") != "active":
        raise AssertionError(f"Manifest status is not 'active': {manifest_data.get('status')}")

    # 2. Validate Safety Policy cryptographic hash
    if policy_path is None:
        policy_path = settings.POLICY_FILE_PATH
    policy_path = Path(policy_path)
    if not policy_path.exists():
        raise FileNotFoundError(f"Safety policy file not found at {policy_path}")

    computed_policy_hash = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    if computed_policy_hash != manifest_data["safety_policy_sha256"]:
        raise AssertionError(
            f"Safety policy SHA-256 hash mismatch: manifest expects {manifest_data['safety_policy_sha256']}, "
            f"computed {computed_policy_hash} from {policy_path}"
        )

    # 3. Validate SQLite chunk repository & release_manifests record
    if db_path is None:
        db_path = settings.SQLITE_DB_PATH
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"SQLite database not found at {db_path}")

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        # 3a. Check release_manifests table record
        cur.execute(
            "SELECT manifest_sha256, status FROM release_manifests WHERE release_id = ?",
            (manifest_data["corpus_release"],),
        )
        db_manifest_row = cur.fetchone()
        if not db_manifest_row:
            raise AssertionError(
                f"SQLite release_manifests table has no entry for release_id '{manifest_data['corpus_release']}'"
            )
        db_manifest_sha256, db_status = db_manifest_row
        if db_manifest_sha256 != manifest_data["manifest_sha256"]:
            raise AssertionError(
                f"Manifest SHA-256 mismatch with SQLite DB: manifest file has {manifest_data['manifest_sha256']}, "
                f"SQLite DB record has {db_manifest_sha256}"
            )
        if db_status != "active":
            raise AssertionError(f"SQLite release_manifests status is not 'active': '{db_status}'")

        # 3b. Fetch all approved child chunks
        cur.execute(
            "SELECT chunk_id, chunk_content_hash FROM child_chunks "
            "WHERE review_status = 'approved' AND superseded_by IS NULL"
        )
        sqlite_approved = dict(cur.fetchall())

        if len(sqlite_approved) != manifest_data["approved_chunks"]:
            raise AssertionError(
                f"Approved chunk count mismatch: SQLite has {len(sqlite_approved)}, "
                f"manifest expects {manifest_data['approved_chunks']}"
            )

        # 3c. Fetch all unapproved / quarantined / superseded chunk IDs
        cur.execute(
            "SELECT chunk_id FROM child_chunks "
            "WHERE review_status != 'approved' OR superseded_by IS NOT NULL"
        )
        unapproved_ids = {row[0] for row in cur.fetchall()}
    finally:
        conn.close()

    # 4. Validate Qdrant collection via paginated scrolling
    if qdrant_path is None:
        qdrant_path = settings.QDRANT_STORAGE_DIR
    qdrant_path = Path(qdrant_path)
    if not qdrant_path.exists():
        raise FileNotFoundError(f"Qdrant storage directory not found at {qdrant_path}")

    if collection_name is None:
        collection_name = manifest_data.get("qdrant_collection", settings.QDRANT_COLLECTION)

    own_client = False
    if client is None:
        # Check if vector_store singleton exists and holds an open client for this path
        try:
            from app.retrieval.vector_store import vector_store
            if (
                vector_store is not None
                and hasattr(vector_store, "client")
                and vector_store.client is not None
                and Path(vector_store.storage_dir).resolve() == qdrant_path.resolve()
            ):
                client = vector_store.client
        except Exception:
            pass

    if client is None:
        client = QdrantClient(path=str(qdrant_path))
        own_client = True

    try:
        # Check collection or alias existence
        collections = [c.name for c in client.get_collections().collections]
        aliases = {a.alias_name: a.collection_name for a in client.get_aliases().aliases}

        if collection_name not in collections and collection_name not in aliases:
            raise AssertionError(
                f"Target collection or alias '{collection_name}' not found in Qdrant. "
                f"Available collections: {collections}, aliases: {list(aliases.keys())}"
            )

        require_sparse = (expected_retrieval_mode == "hybrid")
        if require_sparse:
            coll_info = client.get_collection(collection_name)
            sparse_cfg = getattr(coll_info.config.params, "sparse_vectors", None) or {}
            if "sparse" not in sparse_cfg:
                raise AssertionError(
                    f"Collection '{collection_name}' lacks required 'sparse' vector config for hybrid mode."
                )

        qdrant_points: Dict[str, Dict[str, Any]] = {}
        offset = None

        while True:
            records, next_offset = client.scroll(
                collection_name=collection_name,
                limit=scroll_page_size,
                with_payload=True,
                with_vectors=require_sparse,
                offset=offset,
            )
            for r in records:
                if not r.payload:
                    raise AssertionError(f"Qdrant point {r.id} has no payload")
                chunk_id = r.payload.get("chunk_id")
                if not chunk_id:
                    raise AssertionError(f"Malformed Qdrant point {r.id}: 'chunk_id' is null or missing")
                if chunk_id in qdrant_points:
                    raise AssertionError(f"Duplicate chunk_id found in Qdrant collection: {chunk_id}")
                if require_sparse:
                    vec_map = r.vector if isinstance(r.vector, dict) else {}
                    dense_vec = vec_map.get("dense")
                    sparse_vec = vec_map.get("sparse")
                    if not dense_vec or not sparse_vec or not getattr(sparse_vec, "indices", None):
                        raise AssertionError(
                            f"Qdrant point {chunk_id} is missing non-empty 'dense' or 'sparse' named vector."
                        )
                qdrant_points[chunk_id] = r.payload

            offset = next_offset
            if offset is None:
                break
    finally:
        if own_client and client is not None:
            try:
                client.close()
            except Exception:
                pass
            if hasattr(client, "_client"):
                try:
                    del client._client
                except AttributeError:
                    pass

    # 5. Exact Parity & Integrity Assertions
    # 5a. Vector count
    if len(qdrant_points) != manifest_data["indexed_vectors"]:
        raise AssertionError(
            f"Indexed vector count mismatch: Qdrant has {len(qdrant_points)}, "
            f"manifest expects {manifest_data['indexed_vectors']}"
        )

    # 5b. Exact ID-set equality
    sqlite_ids = set(sqlite_approved.keys())
    qdrant_ids = set(qdrant_points.keys())

    missing_in_qdrant = sqlite_ids - qdrant_ids
    unexpected_in_qdrant = qdrant_ids - sqlite_ids

    if missing_in_qdrant or unexpected_in_qdrant:
        missing_preview = list(missing_in_qdrant)[:5]
        unexpected_preview = list(unexpected_in_qdrant)[:5]
        raise AssertionError(
            f"Qdrant / SQLite ID-set equality violated. "
            f"Missing in Qdrant: {len(missing_in_qdrant)} (samples: {missing_preview}), "
            f"Unexpected in Qdrant: {len(unexpected_in_qdrant)} (samples: {unexpected_preview})"
        )

    # 5c. Point payload metadata & content-hash verification
    for chunk_id, payload in qdrant_points.items():
        if payload.get("review_status") != "approved":
            raise AssertionError(
                f"Qdrant point {chunk_id} has invalid review_status '{payload.get('review_status')}', "
                f"expected 'approved'"
            )
        if payload.get("corpus_release") != manifest_data["corpus_release"]:
            raise AssertionError(
                f"Qdrant point {chunk_id} has corpus_release '{payload.get('corpus_release')}', "
                f"expected '{manifest_data['corpus_release']}'"
            )
        if payload.get("superseded_by") is not None:
            raise AssertionError(
                f"Qdrant point {chunk_id} has active superseded_by marker: {payload.get('superseded_by')}"
            )
        expected_hash = sqlite_approved[chunk_id]
        point_hash = payload.get("chunk_content_hash")
        if point_hash != expected_hash:
            raise AssertionError(
                f"Content hash mismatch for chunk {chunk_id}: "
                f"Qdrant payload has '{point_hash}', SQLite DB has '{expected_hash}'"
            )

    # 5d. Zero Quarantine Leaks
    quarantine_leakage = qdrant_ids & unapproved_ids
    if quarantine_leakage:
        raise AssertionError(
            f"Quarantine leak detected: {len(quarantine_leakage)} unapproved/superseded chunks "
            f"indexed in Qdrant! Examples: {list(quarantine_leakage)[:5]}"
        )

    return {
        "status": "PASSED",
        "corpus_release": manifest_data["corpus_release"],
        "collection_name": collection_name,
        "approved_chunks_count": len(sqlite_approved),
        "indexed_vectors_count": len(qdrant_points),
        "unapproved_quarantined_count": len(unapproved_ids),
        "manifest_sha256": manifest_data["manifest_sha256"],
        "safety_policy_sha256": computed_policy_hash,
    }


def main():
    parser = argparse.ArgumentParser(description="GuardDengue Preflight Parity Suite")
    parser.add_argument("--manifest", type=str, default=None, help="Path to release manifest JSON")
    parser.add_argument("--db", type=str, default=None, help="Path to SQLite chunks DB")
    parser.add_argument("--qdrant", type=str, default=None, help="Path to Qdrant storage directory")
    parser.add_argument("--policy", type=str, default=None, help="Path to safety policy JSON")
    parser.add_argument("--collection", type=str, default=None, help="Qdrant collection name or alias")
    parser.add_argument("--page-size", type=int, default=100, help="Scroll page limit")
    parser.add_argument("--mode", type=str, choices=["dense", "hybrid"], default="dense", help="Expected retrieval mode")
    args = parser.parse_args()

    try:
        res = preflight_release_parity_check(
            manifest_path=args.manifest,
            db_path=args.db,
            qdrant_path=args.qdrant,
            policy_path=args.policy,
            collection_name=args.collection,
            scroll_page_size=args.page_size,
            expected_retrieval_mode=args.mode,
        )
        print(f"[SUCCESS] Preflight Parity Passed: {res['approved_chunks_count']} chunks verified in sync")
        sys.exit(0)
    except Exception as exc:
        print(f"[FAILURE] Preflight Parity Failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
