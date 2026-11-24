"""
GuardDengue — Evaluation Runner & Dense Baseline Test Suite (Phase 7)

Validates:
- score_retrieval_case() logic for single_span, conjunctive, and quarantined query types
- MRR@k reciprocal rank calculations across top-k rank boundaries
- Conjunctive all-or-nothing semantic satisfaction
- Full benchmark execution and scorecard generation against eval_dev_smoke.jsonl
- Gate check assertion logic (Provenance, Span_Recall@5, Ingredient_Recall, Ingredient_Precision,
  Fail_Closed_Rate, Negative_Invariant_Pass_Rate, Completeness_Flag_Accuracy, Latency_p50)
"""

import json
import math
import pytest
import tempfile
from pathlib import Path

from app.core.config import settings
from knowledge_pipeline.eval_runner import score_retrieval_case, run_evaluation


def test_score_retrieval_case_single_span_hit():
    """Verify single_span retrieval scoring when target chunk is hit at various ranks."""
    span_sets = [{"chunk_A", "chunk_B"}]

    # Hit at rank 1
    scores_r1 = score_retrieval_case("single_span", span_sets, ["chunk_A", "chunk_X", "chunk_Y"], top_k=5)
    assert scores_r1["span_recall"] == 1.0
    assert scores_r1["conjunct_recall"] is None
    assert scores_r1["mrr"] == 1.0

    # Hit at rank 3
    scores_r3 = score_retrieval_case("single_span", span_sets, ["chunk_X", "chunk_Y", "chunk_B"], top_k=5)
    assert scores_r3["span_recall"] == 1.0
    assert scores_r3["conjunct_recall"] is None
    assert math.isclose(scores_r3["mrr"], 1.0 / 3.0)

    # Miss beyond top_k
    scores_miss = score_retrieval_case("single_span", span_sets, ["chunk_X", "chunk_Y", "chunk_Z", "chunk_W", "chunk_V", "chunk_A"], top_k=5)
    assert scores_miss["span_recall"] == 0.0
    assert scores_miss["conjunct_recall"] is None
    assert scores_miss["mrr"] == 0.0


def test_score_retrieval_case_conjunctive():
    """Verify conjunctive retrieval scoring requires ALL conjuncts to be satisfied."""
    span_sets = [{"chunk_A"}, {"chunk_B"}]

    # Both present in top-k
    scores_both = score_retrieval_case("conjunctive", span_sets, ["chunk_A", "chunk_B", "chunk_C"], top_k=5)
    assert scores_both["span_recall"] == 1.0
    assert scores_both["conjunct_recall"] == 1.0
    assert scores_both["mrr"] == 1.0  # chunk_A at rank 1

    # Only 1 of 2 present in top-k -> conjunctive fails (0.0), individual span recall is 0.5
    scores_partial = score_retrieval_case("conjunctive", span_sets, ["chunk_A", "chunk_C", "chunk_D"], top_k=5)
    assert scores_partial["span_recall"] == 0.5
    assert scores_partial["conjunct_recall"] == 0.0
    assert scores_partial["mrr"] == 1.0  # first hit is at rank 1, but conjunct is incomplete

    # Neither present in top-k
    scores_none = score_retrieval_case("conjunctive", span_sets, ["chunk_C", "chunk_D", "chunk_E"], top_k=5)
    assert scores_none["span_recall"] == 0.0
    assert scores_none["conjunct_recall"] == 0.0
    assert scores_none["mrr"] == 0.0


def test_score_retrieval_case_quarantined():
    """Verify quarantined queries with empty provenance return None for retrieval metrics."""
    scores = score_retrieval_case("quarantined_coverage", [], ["chunk_A", "chunk_B"], top_k=5)
    assert scores["span_recall"] is None
    assert scores["conjunct_recall"] is None
    assert scores["mrr"] is None


def test_score_retrieval_case_empty_retrieved():
    """Verify handling when retrieval engine returns 0 chunks."""
    span_sets = [{"chunk_A"}]
    scores = score_retrieval_case("single_span", span_sets, [], top_k=5)
    assert scores["span_recall"] == 0.0
    assert scores["conjunct_recall"] is None
    assert scores["mrr"] == 0.0


def test_score_retrieval_case_empty_spans_raises_for_non_quarantined():
    """Verify non-quarantined query with empty provenance raises fail-closed ValueError."""
    with pytest.raises(ValueError, match="must resolve at least 1 expected provenance span"):
        score_retrieval_case("single_span", [], ["chunk_A"], top_k=5)


def test_full_benchmark_run_baseline_mode_passes_invariants():
    """Execute the untainted 30-case smoke benchmark in baseline capture mode (7 invariant gates pass)."""
    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as tf:
        temp_scorecard_path = Path(tf.name)

    try:
        scorecard = run_evaluation(
            benchmark_path=settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl",
            corpus_release="v0.1-dev",
            output_scorecard_path=temp_scorecard_path,
            top_k=5,
            retrieval_mode="dense",
            enforce_retrieval_gate=False,
        )

        assert scorecard["status"] == "PASSED"
        assert scorecard["retrieval_mode"] == "dense"
        assert scorecard["retrieval_gates_enforced"] is False
        assert scorecard["total_cases"] == 30
        assert scorecard["provenance_resolution_failures"] == 0

        # Authentic dense baseline metrics recorded cleanly (~53.4% Span_Recall@5)
        ret = scorecard["metrics"]["retrieval"]
        assert 0.45 <= ret["span_recall_at_5"] < 0.90
        assert ret["mrr_at_5"] > 0.30

        # Completeness metrics
        comp = scorecard["metrics"]["completeness"]
        assert comp["completeness_flag_accuracy"] == 1.0

        # Safety metrics
        med = scorecard["metrics"]["medication_safety"]
        assert med["ingredient_recall"] == 1.0
        assert med["ingredient_precision"] == 1.0
        assert med["detected_terms_accuracy"] == 1.0
        assert med["fail_closed_rate"] == 1.0
        assert med["negative_invariant_pass_rate"] == 1.0

        # Latency
        lat = scorecard["metrics"]["latency_ms"]
        assert lat["p50"] < 30.0

        # All 7 non-retrieval invariant gates must pass
        assert len(scorecard["gates"]) == 7
        for gate in scorecard["gates"]:
            assert gate["passed"] is True, f"Gate failed: {gate['gate_name']} (actual: {gate['actual']}, required: {gate['threshold']})"

        # Verify disk file persistence
        assert temp_scorecard_path.exists()
        disk_data = json.loads(temp_scorecard_path.read_text(encoding="utf-8"))
        assert disk_data["status"] == "PASSED"
        assert disk_data["total_cases"] == 30

        # Strict promotion mode MUST fail when retrieval recall < 0.90
        strict_scorecard = run_evaluation(
            benchmark_path=settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl",
            corpus_release="v0.1-dev",
            output_scorecard_path=temp_scorecard_path,
            top_k=5,
            retrieval_mode="dense",
            enforce_retrieval_gate=True,
        )
        assert strict_scorecard["status"] == "FAILED"
        assert len(strict_scorecard["gates"]) == 9
        span_gate = next(g for g in strict_scorecard["gates"] if g["gate_name"] == "Span_Recall@5")
        assert span_gate["passed"] is False

    finally:
        temp_scorecard_path.unlink(missing_ok=True)
