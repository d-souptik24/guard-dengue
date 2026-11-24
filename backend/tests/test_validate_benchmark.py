"""
GuardDengue — Benchmark Dataset & Validator Test Suite (Phase 6)

Validates:
- eval_dev_smoke.jsonl 100% schema compliance and 0 provenance resolution failures
- Fail-closed behavior on missing fields, invalid query types, invalid slices
- Strict anchor token bounds (5 <= tokens <= 20)
- Provenance anchor resolution against SQLite child chunks
- Zero-provenance enforcement for quarantined queries
- Conjunctive and single-span cardinality constraints
- Minimum cohort size validation
"""

import json
import pytest
import tempfile
from pathlib import Path

from app.core.config import settings
from knowledge_pipeline.validate_benchmark import validate_benchmark


def test_eval_dev_smoke_passes_live():
    """Verify the active eval_dev_smoke.jsonl dataset passes all validation gates with 0 errors."""
    report = validate_benchmark()
    assert report["status"] == "PASSED"
    assert report["total_cases"] == 30
    assert report["failure_count"] == 0
    assert report["failures"] == []


def test_benchmark_missing_required_field():
    """Assert failure when a case is missing a required schema field."""
    case = {
        "eval_id": "TEST_001",
        "query": "What is dengue?",
        # missing query_type, slice, expected_provenance, etc.
    }
    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        tf.write(json.dumps(case) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "missing_required_field" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)


def test_benchmark_anchor_token_count_too_short():
    """Assert failure when anchor has fewer than 5 tokens."""
    with open(settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Make anchor too short (3 tokens)
    cases[0]["expected_provenance"][0]["key_text_anchor"] = "too short anchor"

    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        for c in cases:
            tf.write(json.dumps(c) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "anchor_token_count_out_of_bounds" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)


def test_benchmark_anchor_token_count_too_long():
    """Assert failure when anchor has more than 20 tokens."""
    with open(settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Make anchor 22 tokens long
    cases[0]["expected_provenance"][0]["key_text_anchor"] = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo"

    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        for c in cases:
            tf.write(json.dumps(c) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "anchor_token_count_out_of_bounds" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)


def test_benchmark_unmatched_anchor_resolution_failure():
    """Assert failure when anchor text does not exist in the approved document chunks."""
    with open(settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Replace with non-existent text
    cases[0]["expected_provenance"][0]["key_text_anchor"] = "non existent clinical guideline anchor text not present anywhere"

    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        for c in cases:
            tf.write(json.dumps(c) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "provenance_resolution_failure" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)


def test_benchmark_quarantined_query_must_have_zero_provenance():
    """Assert failure if a quarantined_coverage query defines non-empty expected_provenance."""
    with open(settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Find the quarantined case (SMOKE_027) and inject an anchor
    for c in cases:
        if c.get("query_type") == "quarantined_coverage":
            c["expected_provenance"] = [
                {
                    "doc_id": "who_arboviral_guideline_2025",
                    "section_path": "Case",
                    "page_start": 5,
                    "page_end": 5,
                    "key_text_anchor": "intense and sustained abdominal pain, or tenderness",
                }
            ]
            break

    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        for c in cases:
            tf.write(json.dumps(c) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "quarantined_query_has_provenance" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)


def test_benchmark_conjunctive_cardinality():
    """Assert failure if a conjunctive query defines fewer than 2 spans."""
    with open(settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Find conjunctive case and remove 1 anchor
    for c in cases:
        if c.get("query_type") == "conjunctive":
            c["expected_provenance"] = c["expected_provenance"][:1]
            break

    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        for c in cases:
            tf.write(json.dumps(c) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "conjunctive_count_too_low" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)


def test_benchmark_cohort_size_insufficient():
    """Assert failure if the dataset contains fewer than 30 cases."""
    with open(settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl", "r", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    # Truncate to 10 cases
    truncated = cases[:10]

    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf:
        for c in truncated:
            tf.write(json.dumps(c) + "\n")
        temp_path = Path(tf.name)

    try:
        report = validate_benchmark(dataset_path=temp_path)
        assert report["status"] == "FAILED"
        assert any(f.get("type") == "cohort_size_insufficient" for f in report["failures"])
    finally:
        temp_path.unlink(missing_ok=True)
