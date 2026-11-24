"""
GuardDengue — Production Release Gates & Statistical Certification Test Suite (Phase 8)

Validates:
- compute_mcnemar_paired_test() exact binomial and continuity-corrected chi-square testing
- compute_wilcoxon_paired_test() signed-rank statistical hypothesis testing
- validate_release_gates() against live dense baseline scorecard (all 9 gates pass)
- Fail-closed locked certification gating (rejects dev manifest missing locked SHA-256)
- Cryptographic tamper detection on release benchmark dataset
- A/B non-inferiority validation and regression detection on critical warning sign slices
"""

import copy
import hashlib
import json
import math
import tempfile
from pathlib import Path
import pytest

from app.core.config import settings
from knowledge_pipeline.release_gates import (
    compute_mcnemar_paired_test,
    compute_wilcoxon_paired_test,
    validate_release_gates,
)


def test_mcnemar_identical_distributions():
    """Verify McNemar test returns p=1.0 and significant=False when distributions are identical."""
    baseline = [True, True, False, False, True]
    candidate = [True, True, False, False, True]
    res = compute_mcnemar_paired_test(baseline, candidate)
    assert res["statistic"] == 0.0
    assert res["p_value"] == 1.0
    assert res["significant"] is False
    assert res["contingency"]["candidate_better"] == 0
    assert res["contingency"]["baseline_better"] == 0


def test_mcnemar_discordant_small_exact_binomial():
    """Verify small discordant sample (N < 25) uses exact binomial test."""
    # 10 cases candidate passes where baseline failed, only 1 where baseline passed and candidate failed
    baseline = [False] * 10 + [True] * 1 + [True] * 10
    candidate = [True] * 10 + [False] * 1 + [True] * 10
    res = compute_mcnemar_paired_test(baseline, candidate)
    assert res["method"] == "exact_binomial"
    assert res["p_value"] < 0.05
    assert res["significant"] is True
    assert res["contingency"]["candidate_better"] == 10
    assert res["contingency"]["baseline_better"] == 1


def test_mcnemar_discordant_large_chi2():
    """Verify large discordant sample (N >= 25) uses continuity-corrected chi2."""
    baseline = [False] * 40 + [True] * 10
    candidate = [True] * 40 + [False] * 10
    res = compute_mcnemar_paired_test(baseline, candidate)
    assert res["method"] == "continuity_corrected_chi2"
    assert res["p_value"] < 0.001
    assert res["significant"] is True


def test_wilcoxon_identical_distributions():
    """Verify Wilcoxon signed-rank returns p=1.0 when all differences are zero."""
    baseline = [0.8, 0.5, 1.0, 0.2]
    candidate = [0.8, 0.5, 1.0, 0.2]
    res = compute_wilcoxon_paired_test(baseline, candidate)
    assert res["p_value"] == 1.0
    assert res["significant"] is False
    assert res["mean_difference"] == 0.0


def test_wilcoxon_significant_improvement():
    """Verify Wilcoxon detects statistically significant ranking improvements."""
    baseline = [0.2, 0.25, 0.33, 0.2, 0.1, 0.2, 0.25, 0.15, 0.2, 0.1] * 3
    candidate = [1.0, 1.0, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0, 1.0, 0.5] * 3
    res = compute_wilcoxon_paired_test(baseline, candidate)
    assert res["p_value"] < 0.001
    assert res["significant"] is True
    assert res["mean_difference"] > 0.5


def test_validate_release_gates_live_dense_baseline_modes():
    """Verify baseline_mode=True passes 7 invariant gates while strict promotion fails on ~53.4% dense recall."""
    scorecard_path = settings.KNOWLEDGE_DIR / "dense_baseline_scorecard.json"
    manifest_path = settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json"
    benchmark_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"

    baseline_report = validate_release_gates(
        eval_scorecard_path=scorecard_path,
        manifest_path=manifest_path,
        benchmark_dataset_path=benchmark_path,
        enforce_locked_certification=False,
        baseline_mode=True,
    )

    assert baseline_report["status"] == "PASSED"
    assert len(baseline_report["gates"]) == 7
    for gate in baseline_report["gates"]:
        assert gate["passed"] is True, f"Gate failed: {gate['gate_name']}"

    strict_report = validate_release_gates(
        eval_scorecard_path=scorecard_path,
        manifest_path=manifest_path,
        benchmark_dataset_path=benchmark_path,
        enforce_locked_certification=False,
        baseline_mode=False,
    )
    assert strict_report["status"] == "FAILED"
    assert len(strict_report["gates"]) == 9
    span_gate = next(g for g in strict_report["gates"] if g["gate_name"] == "Span_Recall@5")
    assert span_gate["passed"] is False


def test_validate_release_gates_enforce_locked_fails_dev_manifest():
    """Verify enforce_locked_certification=True fails closed against uncertified dev manifest."""
    scorecard_path = settings.KNOWLEDGE_DIR / "dense_baseline_scorecard.json"
    manifest_path = settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json"
    benchmark_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"

    report = validate_release_gates(
        eval_scorecard_path=scorecard_path,
        manifest_path=manifest_path,
        benchmark_dataset_path=benchmark_path,
        enforce_locked_certification=True,
    )

    assert report["status"] == "FAILED"
    locked_gate = next(g for g in report["gates"] if g["gate_name"] == "Locked_Holdout_Certification")
    assert locked_gate["passed"] is False


def test_validate_release_gates_enforce_locked_succeeds_when_signed():
    """Verify locked certification passes when candidate meets release thresholds and manifest SHA-256 is signed."""
    scorecard_path = settings.KNOWLEDGE_DIR / "dense_baseline_scorecard.json"
    manifest_path = settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json"
    benchmark_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"

    # Build a synthetic passing release candidate scorecard (e.g. Phase 8A hybrid candidate >= 0.90)
    passing_scorecard = copy.deepcopy(json.loads(scorecard_path.read_text(encoding="utf-8")))
    passing_scorecard["metrics"]["retrieval"]["span_recall_at_5"] = 0.9655
    passing_scorecard["metrics"]["retrieval"]["conjunct_recall_at_5"] = 1.0

    actual_hash = hashlib.sha256(benchmark_path.read_bytes()).hexdigest()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_data["locked_benchmark_sha256"] = actual_hash
    manifest_data["release_certified"] = True

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as tf_s:
        tf_s.write(json.dumps(passing_scorecard))
        temp_scorecard_path = Path(tf_s.name)

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as tf_m:
        tf_m.write(json.dumps(manifest_data))
        temp_manifest_path = Path(tf_m.name)

    try:
        report = validate_release_gates(
            eval_scorecard_path=temp_scorecard_path,
            manifest_path=temp_manifest_path,
            benchmark_dataset_path=benchmark_path,
            enforce_locked_certification=True,
        )

        assert report["status"] == "PASSED"
        locked_gate = next(g for g in report["gates"] if g["gate_name"] == "Locked_Holdout_Certification")
        assert locked_gate["passed"] is True
    finally:
        temp_scorecard_path.unlink(missing_ok=True)
        temp_manifest_path.unlink(missing_ok=True)


def test_validate_release_gates_detects_tampered_benchmark():
    """Verify cryptographic check detects even a single-byte alteration to the benchmark dataset."""
    scorecard_path = settings.KNOWLEDGE_DIR / "dense_baseline_scorecard.json"
    manifest_path = settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json"
    benchmark_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"

    # Create signed manifest with original hash
    actual_hash = hashlib.sha256(benchmark_path.read_bytes()).hexdigest()
    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_data["locked_benchmark_sha256"] = actual_hash
    manifest_data["release_certified"] = True

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as tf_m:
        tf_m.write(json.dumps(manifest_data))
        temp_manifest_path = Path(tf_m.name)

    # Create tampered benchmark file (appended newline or comment)
    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False, encoding="utf-8") as tf_b:
        tf_b.write(benchmark_path.read_text(encoding="utf-8") + " ")
        temp_benchmark_path = Path(tf_b.name)

    try:
        report = validate_release_gates(
            eval_scorecard_path=scorecard_path,
            manifest_path=temp_manifest_path,
            benchmark_dataset_path=temp_benchmark_path,
            enforce_locked_certification=True,
        )

        assert report["status"] == "FAILED"
        locked_gate = next(g for g in report["gates"] if g["gate_name"] == "Locked_Holdout_Certification")
        assert locked_gate["passed"] is False
        assert "Benchmark SHA-256 mismatch" in str(locked_gate["actual"])
    finally:
        temp_manifest_path.unlink(missing_ok=True)
        temp_benchmark_path.unlink(missing_ok=True)


def test_validate_release_gates_ab_non_inferiority_and_none_exclusion():
    """Verify A/B gate excludes quarantined None cases (paired=29), catches regressions, and checks significance."""
    scorecard_path = settings.KNOWLEDGE_DIR / "dense_baseline_scorecard.json"
    manifest_path = settings.KNOWLEDGE_DIR / "release_manifest_v0.1-dev.json"
    benchmark_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"

    base_data = json.loads(scorecard_path.read_text(encoding="utf-8"))

    # Case 1: Degraded candidate that regressed on a severe warning sign case
    regressed_data = copy.deepcopy(base_data)
    for c in regressed_data["detailed_case_results"]:
        if c["slice"] == "warning_signs_severe" and c["span_recall"] == 1.0:
            c["span_recall"] = 0.0
            break

    # Case 2: Strong improved candidate where all misses flip to hits and MRRs improve
    improved_data = copy.deepcopy(base_data)
    for c in improved_data["detailed_case_results"]:
        if c["span_recall"] is not None:
            c["span_recall"] = 1.0
            c["mrr"] = max(float(c["mrr"] or 0.0), 0.9)
    improved_data["metrics"]["retrieval"]["span_recall_at_5"] = 1.0
    improved_data["metrics"]["retrieval"]["conjunct_recall_at_5"] = 1.0

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as tf_reg:
        tf_reg.write(json.dumps(regressed_data))
        temp_reg_path = Path(tf_reg.name)

    with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False, encoding="utf-8") as tf_imp:
        tf_imp.write(json.dumps(improved_data))
        temp_imp_path = Path(tf_imp.name)

    try:
        reg_report = validate_release_gates(
            eval_scorecard_path=temp_reg_path,
            manifest_path=manifest_path,
            benchmark_dataset_path=benchmark_path,
            baseline_scorecard_path=scorecard_path,
            enforce_locked_certification=False,
            baseline_mode=True,
        )

        assert reg_report["status"] == "FAILED"
        # SMOKE_027 (quarantined_coverage, span_recall=None) must be excluded -> 29 paired cases
        assert reg_report["ab_comparison"]["paired_cases_count"] == 29
        ab_gate = next(g for g in reg_report["gates"] if g["gate_name"] == "A_B_Non_Inferiority")
        assert ab_gate["passed"] is False

        imp_report = validate_release_gates(
            eval_scorecard_path=temp_imp_path,
            manifest_path=manifest_path,
            benchmark_dataset_path=benchmark_path,
            baseline_scorecard_path=scorecard_path,
            enforce_locked_certification=False,
            baseline_mode=False,
            enforce_ab_significance=True,
        )
        assert imp_report["status"] == "PASSED"
        assert imp_report["ab_comparison"]["paired_cases_count"] == 29
        mcnemar_gate = next(g for g in imp_report["gates"] if g["gate_name"] == "A_B_McNemar_Significance")
        wilcoxon_gate = next(g for g in imp_report["gates"] if g["gate_name"] == "A_B_Wilcoxon_Significance")
        assert mcnemar_gate["passed"] is True
        assert wilcoxon_gate["passed"] is True
    finally:
        temp_reg_path.unlink(missing_ok=True)
        temp_imp_path.unlink(missing_ok=True)
