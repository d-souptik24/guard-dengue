"""
GuardDengue — Benchmark Dataset Validator & Provenance Resolver (Phase 6)

Validates the integrity, schema conformance, and document grounding of evaluation datasets
such as eval_dev_smoke.jsonl. Enforces:
- Schema adherence across all 30 test cases
- Strict anchor token bounds (5 to 20 tokens per anchor)
- 0 provenance resolution failures against approved SQLite child chunks
- Zero-provenance enforcement for quarantined queries (quarantined_coverage)
"""

import json
import sqlite3
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings

VALID_QUERY_TYPES = {"single_span", "conjunctive", "quarantined_coverage"}
VALID_SLICES = {
    "diagnostic_timing",
    "warning_signs_severe",
    "tables_flowcharts",
    "medication_safety",
    "quarantined_incomplete",
}
VALID_COVERAGE_STATUSES = {"complete", "partial", "unavailable"}
VALID_ACTION_CODES = {
    "AVOID_NSAID_CONTRAINDICATED",
    "AVOID_FDC_CONTRAINDICATED",
    "ESCALATE_UNKNOWN_MEDICATION",
    "DETECTOR_UNCERTAIN",
    "CHRONIC_PRESCRIPTION_ESCALATE",
    "NEGATED_MENTION_EDUCATION",
    "STANDARD_EVIDENCE_RETRIEVAL",
}


def normalize_whitespace(text: str) -> str:
    """Collapses consecutive whitespace characters into a single space."""
    return " ".join(text.split())


def resolve_provenance_to_chunks(
    conn: sqlite3.Connection,
    doc_id: str,
    page_start: int,
    page_end: int,
    text_anchor: str,
    section_path: Optional[str] = None,
) -> List[str]:
    """
    Dynamically resolves a document anchor to matching approved SQLite chunk IDs.
    Returns list of chunk_ids that contain the normalized anchor text within the page range.
    """
    cur = conn.cursor()
    # Query all approved chunks within the target document and page range
    cur.execute(
        "SELECT chunk_id, text, section_path FROM child_chunks "
        "WHERE doc_id = ? AND page_start <= ? AND page_end >= ? "
        "AND review_status = 'approved' AND superseded_by IS NULL",
        (doc_id, page_end, page_start),
    )
    rows = cur.fetchall()

    norm_anchor = normalize_whitespace(text_anchor).lower()
    matching_chunk_ids = []

    for chunk_id, chunk_text, s_path in rows:
        norm_chunk = normalize_whitespace(chunk_text).lower()
        if norm_anchor in norm_chunk:
            matching_chunk_ids.append(chunk_id)

    return matching_chunk_ids


def validate_benchmark(
    dataset_path: Optional[Path | str] = None,
    db_path: Optional[Path | str] = None,
) -> Dict[str, Any]:
    """
    Validates benchmark dataset JSONL against schema and SQLite approved chunks.
    Raises AssertionError if any validation rule or anchor resolution fails.
    """
    if dataset_path is None:
        dataset_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"
    dataset_path = Path(dataset_path)

    if not dataset_path.exists():
        raise FileNotFoundError(f"Benchmark dataset not found at {dataset_path}")

    if db_path is None:
        db_path = settings.SQLITE_DB_PATH
    db_path = Path(db_path)

    if not db_path.exists():
        raise FileNotFoundError(f"SQLite DB not found at {db_path}")

    conn = sqlite3.connect(db_path)
    failures: List[Dict[str, Any]] = []
    cases: List[Dict[str, Any]] = []

    try:
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f, start=1):
                raw = line.strip()
                if not raw:
                    continue
                try:
                    case = json.loads(raw)
                    cases.append(case)
                except Exception as e:
                    failures.append({
                        "line": line_idx,
                        "type": "json_parse_error",
                        "message": str(e),
                    })
                    continue

                eval_id = case.get("eval_id", f"LINE_{line_idx}")

                # Required fields
                req_fields = [
                    "eval_id",
                    "query",
                    "query_type",
                    "slice",
                    "expected_provenance",
                    "expected_coverage",
                    "expected_medication",
                ]
                for rf in req_fields:
                    if rf not in case:
                        failures.append({
                            "eval_id": eval_id,
                            "type": "missing_required_field",
                            "field": rf,
                        })

                # Validate query_type and slice
                q_type = case.get("query_type")
                if q_type not in VALID_QUERY_TYPES:
                    failures.append({
                        "eval_id": eval_id,
                        "type": "invalid_query_type",
                        "value": q_type,
                    })

                slice_val = case.get("slice")
                if slice_val not in VALID_SLICES:
                    failures.append({
                        "eval_id": eval_id,
                        "type": "invalid_slice",
                        "value": slice_val,
                    })

                # Validate expected_coverage
                cov = case.get("expected_coverage", {})
                if cov.get("coverage_status") not in VALID_COVERAGE_STATUSES:
                    failures.append({
                        "eval_id": eval_id,
                        "type": "invalid_coverage_status",
                        "value": cov.get("coverage_status"),
                    })
                if not isinstance(cov.get("coverage_reason_codes"), list):
                    failures.append({
                        "eval_id": eval_id,
                        "type": "invalid_coverage_reason_codes",
                        "value": cov.get("coverage_reason_codes"),
                    })

                # Validate expected_medication
                med = case.get("expected_medication", {})
                if med.get("action_code") not in VALID_ACTION_CODES:
                    failures.append({
                        "eval_id": eval_id,
                        "type": "invalid_action_code",
                        "value": med.get("action_code"),
                    })
                if not isinstance(med.get("detected_terms"), list):
                    failures.append({"eval_id": eval_id, "type": "invalid_detected_terms"})
                if not isinstance(med.get("canonical_ingredients"), list):
                    failures.append({"eval_id": eval_id, "type": "invalid_canonical_ingredients"})
                if not isinstance(med.get("negative_invariants_passed"), bool):
                    failures.append({"eval_id": eval_id, "type": "invalid_negative_invariants_passed"})

                # Validate expected_provenance
                prov_list = case.get("expected_provenance", [])
                if not isinstance(prov_list, list):
                    failures.append({"eval_id": eval_id, "type": "expected_provenance_not_a_list"})
                    continue

                if q_type == "quarantined_coverage":
                    if len(prov_list) != 0:
                        failures.append({
                            "eval_id": eval_id,
                            "type": "quarantined_query_has_provenance",
                            "count": len(prov_list),
                        })
                elif q_type == "single_span":
                    if len(prov_list) != 1:
                        failures.append({
                            "eval_id": eval_id,
                            "type": "single_span_count_mismatch",
                            "expected": 1,
                            "actual": len(prov_list),
                        })
                elif q_type == "conjunctive":
                    if len(prov_list) < 2:
                        failures.append({
                            "eval_id": eval_id,
                            "type": "conjunctive_count_too_low",
                            "expected_min": 2,
                            "actual": len(prov_list),
                        })

                # Validate individual anchors and resolve against SQLite
                for a_idx, anchor in enumerate(prov_list):
                    for af in ["doc_id", "page_start", "page_end", "key_text_anchor"]:
                        if af not in anchor:
                            failures.append({
                                "eval_id": eval_id,
                                "type": "anchor_missing_field",
                                "field": af,
                                "anchor_idx": a_idx,
                            })

                    text_anchor = anchor.get("key_text_anchor", "")
                    tokens = text_anchor.strip().split()
                    if not (5 <= len(tokens) <= 20):
                        failures.append({
                            "eval_id": eval_id,
                            "type": "anchor_token_count_out_of_bounds",
                            "anchor_idx": a_idx,
                            "token_count": len(tokens),
                            "anchor": text_anchor,
                        })

                    # Resolve anchor in SQLite
                    matched_cids = resolve_provenance_to_chunks(
                        conn=conn,
                        doc_id=anchor.get("doc_id", ""),
                        page_start=anchor.get("page_start", 0),
                        page_end=anchor.get("page_end", 999),
                        text_anchor=text_anchor,
                        section_path=anchor.get("section_path"),
                    )

                    if not matched_cids:
                        failures.append({
                            "eval_id": eval_id,
                            "type": "provenance_resolution_failure",
                            "anchor_idx": a_idx,
                            "doc_id": anchor.get("doc_id"),
                            "pages": (anchor.get("page_start"), anchor.get("page_end")),
                            "anchor": text_anchor,
                        })
    finally:
        conn.close()

    total_cases = len(cases)
    if total_cases < 30:
        failures.append({
            "type": "cohort_size_insufficient",
            "expected_min": 30,
            "actual": total_cases,
        })

    return {
        "status": "PASSED" if not failures else "FAILED",
        "dataset_file": str(dataset_path),
        "total_cases": total_cases,
        "failure_count": len(failures),
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser(description="GuardDengue Benchmark Dataset Validator")
    parser.add_argument("--file", type=str, default=None, help="Path to evaluation JSONL benchmark")
    parser.add_argument("--db", type=str, default=None, help="Path to SQLite database")
    args = parser.parse_args()

    try:
        report = validate_benchmark(dataset_path=args.file, db_path=args.db)
        if report["status"] == "PASSED":
            print(
                f"[SUCCESS] Benchmark Validation Passed: {report['total_cases']} cases validated, "
                f"0 provenance resolution failures."
            )
            sys.exit(0)
        else:
            print(
                f"[FAILURE] Benchmark Validation Failed: {report['failure_count']} errors detected across "
                f"{report['total_cases']} cases.",
                file=sys.stderr,
            )
            for f in report["failures"][:10]:
                print(f"  - {f}", file=sys.stderr)
            sys.exit(1)
    except Exception as exc:
        print(f"[FATAL] Benchmark validator failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
