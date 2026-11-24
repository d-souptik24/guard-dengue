"""
GuardDengue — Phase 1 Verification Script
Validates environment, store paths, manifest synchronization, and Qdrant alias.
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
import sqlite3
import json
import hashlib
from qdrant_client import QdrantClient

def verify_phase1():
    print("--- Phase 1 Verification ---")
    
    # 1. SQLite DB check
    print(f"SQLite DB path: {settings.SQLITE_DB_PATH}")
    assert settings.SQLITE_DB_PATH.exists(), f"SQLite DB missing at {settings.SQLITE_DB_PATH}"
    
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM child_chunks WHERE review_status = 'approved'")
    chunk_count = cur.fetchone()[0]
    print(f"Approved child chunks: {chunk_count}")
    assert chunk_count == 425, f"Expected 425 approved chunks, got {chunk_count}"
    
    # Check release_manifests table in DB
    cur.execute("SELECT manifest_sha256, status FROM release_manifests WHERE release_id = 'v0.1-dev'")
    db_manifest = cur.fetchone()
    assert db_manifest is not None, "No record in release_manifests for v0.1-dev"
    print(f"DB manifest sha256: {db_manifest[0]} (status: {db_manifest[1]})")
    
    # 2. Manifest file on disk
    manifest_path = settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json"
    print(f"Manifest file on disk: {manifest_path}")
    assert manifest_path.exists(), f"Manifest file missing at {manifest_path}"
    
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest_data["manifest_sha256"] == db_manifest[0], "Manifest SHA256 mismatch with SQLite"
    
    # 3. Policy file hash check
    policy_bytes = settings.POLICY_FILE_PATH.read_bytes()
    computed_policy_hash = hashlib.sha256(policy_bytes).hexdigest()
    assert manifest_data["safety_policy_sha256"] == computed_policy_hash, "Policy hash mismatch"
    print(f"Policy SHA256 verified: {computed_policy_hash}")
    
    # 4. Qdrant storage & alias check
    print(f"Qdrant storage path: {settings.QDRANT_STORAGE_DIR}")
    assert settings.QDRANT_STORAGE_DIR.exists(), f"Qdrant dir missing at {settings.QDRANT_STORAGE_DIR}"
    
    qc = QdrantClient(path=str(settings.QDRANT_STORAGE_DIR))
    try:
        collections = [c.name for c in qc.get_collections().collections]
        print(f"Collections: {collections}")
        assert "guarddengue_v0.1-dev" in collections, "Base collection guarddengue_v0.1-dev missing"
        
        aliases = [(a.alias_name, a.collection_name) for a in qc.get_aliases().aliases]
        print(f"Aliases: {aliases}")
        assert any(a[0] == "guarddengue_v0.1-dev_dense" for a in aliases), "Alias guarddengue_v0.1-dev_dense missing"
        
        pts, _ = qc.scroll(collection_name="guarddengue_v0.1-dev_dense", limit=5)
        print(f"Points fetched via alias: {len(pts)}")
        assert len(pts) == 5, f"Expected 5 points via alias scroll, got {len(pts)}"
    finally:
        qc.close()
        
    print("\n[SUCCESS] Phase 1 Verification: ALL CHECKS PASSED")

if __name__ == "__main__":
    verify_phase1()
