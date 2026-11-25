"""
GuardDengue — SQLite Knowledge Base Storage Adapter (Zone 4)

Interfaces directly with guarddengue_chunks.db created by Module 2.
Retrieves full parent chunk text, child chunk records, and corpus release manifests.
"""
import json
import sqlite3
from typing import Any
from app.core.config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.SQLITE_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def get_parent_chunk(parent_id: str) -> dict[str, Any] | None:
    """Fetches broad parent chunk context by parent_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT parent_id, doc_id, section_path, title, level, text, token_count, corpus_release
            FROM parent_chunks
            WHERE parent_id = ?
            """,
            (parent_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def get_child_chunk(chunk_id: str) -> dict[str, Any] | None:
    """Fetches atomic child chunk record by chunk_id."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT chunk_id, parent_id, doc_id, chunk_type, element_type, text,
                   section_path, page_start, page_end, review_status, reviewed_by,
                   superseded_by, chunk_content_hash, metadata_json
            FROM child_chunks
            WHERE chunk_id = ?
            """,
            (chunk_id,)
        )
        row = cursor.fetchone()
        if row:
            data = dict(row)
            if data.get("metadata_json"):
                try:
                    data["metadata"] = json.loads(data["metadata_json"])
                except Exception:
                    data["metadata"] = {}
            return data
    return None

def get_active_corpus_release() -> str:
    """Returns the currently active corpus release tag from release_manifests."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT release_id FROM release_manifests
                WHERE status = 'active'
                ORDER BY promoted_at DESC LIMIT 1
                """
            )
            row = cursor.fetchone()
            if row:
                return row["release_id"]
    except Exception:
        pass
    return settings.CORPUS_RELEASE
