"""
GuardDengue — Production Release Gates & Statistical Certification Engine (Phase 8)

Validates:
1. Cryptographic Benchmark Integrity: Computes SHA-256 of the evaluation benchmark dataset.
2. Production Locked Certification Gate: Enforces fail-closed validation when `enforce_locked_certification=True`
   (asserts `locked_benchmark_sha256` in release manifest matching the benchmark file).
3. Non-Negotiable Release Gates:
   - Provenance_Resolution_Failures == 0
   - Span_Recall@5 >= min_span_recall (default: 0.90)
   - Conjunct_Recall@5 >= min_conjunct_recall (default: 0.85)
   - Ingredient_Recall == 1.00 (within math.isclose epsilon 1e-5)
   - Ingredient_Precision == 1.00 (within math.isclose epsilon 1e-5)
   - Fail_Closed_Rate == 1.00 (within math.isclose epsilon 1e-5)
   - Negative_Invariant_Pass_Rate == 1.00 (within math.isclose epsilon 1e-5)
   - Completeness_Flag_Accuracy == 1.00 (within math.isclose epsilon 1e-5)
   - Latency_p50_ms < max_p50_latency_ms (default: 30.0 ms)
4. Comparative A/B Statistical Hypothesis Testing (Hybrid Candidate vs. Dense Baseline):
   - McNemar's paired test for binary span recall (contingency matrix, continuity correction, p < 0.05).
   - Wilcoxon signed-rank test for continuous MRR differences (p < 0.05).
   - Non-inferiority assurance: 0 regressions on critical warning signs or medication safety invariants.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from scipy import stats

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings


def compute_mcnemar_paired_test(
    baseline_passes: List[bool],
    candidate_passes: List[bool],
) -> Dict[str, Any]:
    """
    Computes McNemar's paired test on binary case outcomes (e.g. span satisfaction).
    Uses exact binomial test when discordant pairs (b + c) < 25,
    otherwise uses Edwards continuity-corrected chi-square test.
    """
    if len(baseline_passes) != len(candidate_passes):
        raise ValueError("Baseline and candidate must have identical length for paired testing.")

    # 2x2 Contingency table
    # a: both pass, b: candidate passes / baseline fails, c: baseline passes / candidate fails, d: both fail
    a = sum(1 for b, c in zip(baseline_passes, candidate_passes) if b and c)
    b = sum(1 for b, c in zip(baseline_passes, candidate_passes) if (not b) and c)
    c = sum(1 for b, c in zip(baseline_passes, candidate_passes) if b and (not c))
    d = sum(1 for b, c in zip(baseline_passes, candidate_passes) if (not b) and (not c))

    discordant = b + c
    if discordant == 0:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "method": "exact_zero_discordance",
            "contingency": {"both_pass": a, "candidate_better": b, "baseline_better": c, "both_fail": d},
            "significant": False,
        }

    if discordant < 25:
        # Exact two-sided binomial test under H0: p = 0.5
        binom_res = stats.binomtest(b, n=discordant, p=0.5, alternative="two-sided")
        p_val = float(binom_res.pvalue)
        stat = float(b)
        method = "exact_binomial"
    else:
        # Continuity-corrected McNemar chi-squared: (|b - c| - 1)^2 / (b + c)
        chi2_stat = ((abs(b - c) - 1.0) ** 2) / float(discordant)
        p_val = float(1.0 - stats.chi2.cdf(chi2_stat, df=1))
        stat = float(chi2_stat)
        method = "continuity_corrected_chi2"

    return {
        "statistic": stat,
        "p_value": p_val,
        "method": method,
        "contingency": {"both_pass": a, "candidate_better": b, "baseline_better": c, "both_fail": d},
        "significant": p_val < 0.05,
    }


def compute_wilcoxon_paired_test(
    baseline_values: List[float],
    candidate_values: List[float],
) -> Dict[str, Any]:
    """
    Computes Wilcoxon signed-rank test on continuous paired scores (e.g. MRR@5).
    Gracefully handles zero-difference distributions.
    """
    if len(baseline_values) != len(candidate_values):
        raise ValueError("Baseline and candidate must have identical length for paired testing.")

    diffs = [c - b for b, c in zip(baseline_values, candidate_values)]
    non_zero_diffs = [d for d in diffs if abs(d) > 1e-9]

    if not non_zero_diffs:
        return {
            "statistic": 0.0,
            "p_value": 1.0,
            "method": "zero_differences",
            "mean_difference": 0.0,
            "significant": False,
        }

    try:
        w_res = stats.wilcoxon(candidate_values, baseline_values, alternative="two-sided")
        p_val = float(w_res.pvalue)
        stat = float(w_res.statistic)
    except Exception:
        stat = 0.0
        p_val = 1.0

    return {
        "statistic": stat,
        "p_value": p_val,
        "method": "wilcoxon_signed_rank",
        "mean_difference": float(np.mean(diffs)),
        "significant": p_val < 0.05,
    }


def evaluate_scorecard_gates(
    *,
    provenance_failures: int,
    ing_recall: float,
    ing_precision: float,
    fail_closed: float,
    neg_invariants: float,
    completeness_acc: float,
    p50_latency: float,
    span_recall: float,
    conjunct_recall: float,
    include_retrieval_gates: bool = True,
    min_span_recall: float = 0.90,
    min_conjunct_recall: float = 0.85,
    max_p50_latency_ms: float = 30.0,
) -> List[Dict[str, Any]]:
    """Evaluates the 7 invariant release gates plus optional retrieval recall gates."""
    gate_evaluations: List[Dict[str, Any]] = [
        {
            "gate_name": "Provenance_Resolution_Failures",
            "passed": (provenance_failures == 0),
            "threshold": 0,
            "actual": provenance_failures,
        },
        {
            "gate_name": "Ingredient_Recall",
            "passed": math.isclose(ing_recall, 1.0, abs_tol=1e-5),
            "threshold": 1.00,
            "actual": round(ing_recall, 4),
        },
        {
            "gate_name": "Ingredient_Precision",
            "passed": math.isclose(ing_precision, 1.0, abs_tol=1e-5),
            "threshold": 1.00,
            "actual": round(ing_precision, 4),
        },
        {
            "gate_name": "Fail_Closed_Rate",
            "passed": math.isclose(fail_closed, 1.0, abs_tol=1e-5),
            "threshold": 1.00,
            "actual": round(fail_closed, 4),
        },
        {
            "gate_name": "Negative_Invariant_Pass_Rate",
            "passed": math.isclose(neg_invariants, 1.0, abs_tol=1e-5),
            "threshold": 1.00,
            "actual": round(neg_invariants, 4),
        },
        {
            "gate_name": "Completeness_Flag_Accuracy",
            "passed": math.isclose(completeness_acc, 1.0, abs_tol=1e-5),
            "threshold": 1.00,
            "actual": round(completeness_acc, 4),
        },
        {
            "gate_name": "Latency_p50_ms",
            "passed": (p50_latency < max_p50_latency_ms),
            "threshold": f"< {max_p50_latency_ms} ms",
            "actual": round(p50_latency, 2),
        },
    ]

    if include_retrieval_gates:
        gate_evaluations.extend([
            {
                "gate_name": "Span_Recall@5",
                "passed": (span_recall >= min_span_recall),
                "threshold": f">= {min_span_recall}",
                "actual": round(span_recall, 4),
            },
            {
                "gate_name": "Conjunct_Recall@5",
                "passed": (conjunct_recall >= min_conjunct_recall),
                "threshold": f">= {min_conjunct_recall}",
                "actual": round(conjunct_recall, 4),
            },
        ])

    return gate_evaluations


def validate_release_gates(
    eval_scorecard_path: str | Path,
    manifest_path: str | Path,
    benchmark_dataset_path: str | Path,
    baseline_scorecard_path: Optional[str | Path] = None,
    enforce_locked_certification: bool = False,
    baseline_mode: bool = False,
    enforce_ab_significance: bool = False,
    min_span_recall: float = 0.90,
    min_conjunct_recall: float = 0.85,
    max_p50_latency_ms: float = 30.0,
) -> Dict[str, Any]:
    """
    Executes production release gate verification against an evaluation scorecard.
    Fails closed immediately if cryptographic integrity is violated or any gate fails.
    When baseline_mode=True, verifies non-retrieval safety/completeness/latency invariants
    while treating Span_Recall@5 and Conjunct_Recall@5 as recorded baseline telemetry.
    """
    scorecard_file = Path(eval_scorecard_path)
    manifest_file = Path(manifest_path)
    benchmark_file = Path(benchmark_dataset_path)

    if not scorecard_file.exists():
        raise SystemExit(f"Release Gate FAILED: Scorecard missing at '{scorecard_file}'.")
    if not manifest_file.exists():
        raise SystemExit(f"Release Gate FAILED: Release manifest missing at '{manifest_file}'.")
    if not benchmark_file.exists():
        raise SystemExit(f"Release Gate FAILED: Benchmark dataset missing at '{benchmark_file}'.")

    scorecard: Dict[str, Any] = json.loads(scorecard_file.read_text(encoding="utf-8"))
    manifest: Dict[str, Any] = json.loads(manifest_file.read_text(encoding="utf-8"))

    # 1. Cryptographic Benchmark Hash Verification
    actual_benchmark_sha256 = hashlib.sha256(benchmark_file.read_bytes()).hexdigest()

    # 2. Production Locked Holdout Gate
    locked_certification_passed = True
    locked_fail_reason = None
    if enforce_locked_certification:
        expected_locked_sha256 = manifest.get("locked_benchmark_sha256")
        if not expected_locked_sha256:
            locked_certification_passed = False
            locked_fail_reason = "Manifest missing required 'locked_benchmark_sha256' for production certification."
        elif expected_locked_sha256 != actual_benchmark_sha256:
            locked_certification_passed = False
            locked_fail_reason = (
                f"Benchmark SHA-256 mismatch! Manifest={expected_locked_sha256}, Actual={actual_benchmark_sha256}."
            )
        elif manifest.get("release_certified") is not True:
            locked_certification_passed = False
            locked_fail_reason = "Manifest field 'release_certified' is not True."

    # 3. Non-Negotiable Release Metric Gates
    metrics = scorecard.get("metrics", {})
    ret_metrics = metrics.get("retrieval", {})
    comp_metrics = metrics.get("completeness", {})
    med_metrics = metrics.get("medication_safety", {})
    lat_metrics = metrics.get("latency_ms", {})

    provenance_failures = scorecard.get("provenance_resolution_failures", 0)
    span_recall = ret_metrics.get("span_recall_at_5", 0.0)
    conjunct_recall = ret_metrics.get("conjunct_recall_at_5", 0.0)
    completeness_acc = comp_metrics.get("completeness_flag_accuracy", 0.0)
    ing_recall = med_metrics.get("ingredient_recall", 0.0)
    ing_precision = med_metrics.get("ingredient_precision", 0.0)
    fail_closed = med_metrics.get("fail_closed_rate", 0.0)
    neg_invariants = med_metrics.get("negative_invariant_pass_rate", 0.0)
    p50_latency = lat_metrics.get("p50", 999.0)

    gate_evaluations = evaluate_scorecard_gates(
        provenance_failures=provenance_failures,
        ing_recall=ing_recall,
        ing_precision=ing_precision,
        fail_closed=fail_closed,
        neg_invariants=neg_invariants,
        completeness_acc=completeness_acc,
        p50_latency=p50_latency,
        span_recall=span_recall,
        conjunct_recall=conjunct_recall,
        include_retrieval_gates=(not baseline_mode),
        min_span_recall=min_span_recall,
        min_conjunct_recall=min_conjunct_recall,
        max_p50_latency_ms=max_p50_latency_ms,
    )

    if enforce_locked_certification:
        gate_evaluations.append({
            "gate_name": "Locked_Holdout_Certification",
            "passed": locked_certification_passed,
            "threshold": "Cryptographically Locked SHA-256",
            "actual": "VALID" if locked_certification_passed else str(locked_fail_reason),
        })

    all_metric_gates_passed = all(g["passed"] for g in gate_evaluations)

    # 4. Comparative A/B Statistical Analysis (if baseline scorecard provided)
    ab_comparison: Optional[Dict[str, Any]] = None
    if baseline_scorecard_path is not None:
        base_file = Path(baseline_scorecard_path)
        if not base_file.exists():
            raise SystemExit(f"Release Gate FAILED: Baseline scorecard missing at '{base_file}'.")
        base_scorecard: Dict[str, Any] = json.loads(base_file.read_text(encoding="utf-8"))

        cand_cases = {c["eval_id"]: c for c in scorecard.get("detailed_case_results", [])}
        base_cases = {c["eval_id"]: c for c in base_scorecard.get("detailed_case_results", [])}

        common_ids = sorted(set(cand_cases.keys()) & set(base_cases.keys()))
        # Filter strictly to eligible retrieval cases (exclude quarantined_coverage where span_recall is None)
        eligible_ids = [
            cid for cid in common_ids
            if base_cases[cid].get("span_recall") is not None and cand_cases[cid].get("span_recall") is not None
        ]
        if eligible_ids:
            base_spans = [float(base_cases[cid]["span_recall"]) >= 1.0 for cid in eligible_ids]
            cand_spans = [float(cand_cases[cid]["span_recall"]) >= 1.0 for cid in eligible_ids]
            mcnemar_res = compute_mcnemar_paired_test(base_spans, cand_spans)

            base_mrrs = [float(base_cases[cid].get("mrr") or 0.0) for cid in eligible_ids]
            cand_mrrs = [float(cand_cases[cid].get("mrr") or 0.0) for cid in eligible_ids]
            wilcoxon_res = compute_wilcoxon_paired_test(base_mrrs, cand_mrrs)

            # Non-inferiority check across warning signs and medication safety invariants
            warning_cids = [cid for cid in eligible_ids if cand_cases[cid].get("slice") == "warning_signs_severe"]
            warning_regressions = [
                cid for cid in warning_cids
                if float(cand_cases[cid]["span_recall"]) < float(base_cases[cid]["span_recall"])
            ]

            base_med = base_scorecard.get("metrics", {}).get("medication_safety", {})
            safety_non_inferior = (
                (ing_recall >= base_med.get("ingredient_recall", 0.0))
                and (ing_precision >= base_med.get("ingredient_precision", 0.0))
                and (fail_closed >= base_med.get("fail_closed_rate", 0.0))
                and (neg_invariants >= base_med.get("negative_invariant_pass_rate", 0.0))
                and (len(warning_regressions) == 0)
            )

            ab_comparison = {
                "paired_cases_count": len(eligible_ids),
                "mcnemar_test": mcnemar_res,
                "wilcoxon_test": wilcoxon_res,
                "warning_sign_regressions": warning_regressions,
                "safety_non_inferior": safety_non_inferior,
            }

            # Enforce non-inferiority as a release requirement
            gate_evaluations.append({
                "gate_name": "A_B_Non_Inferiority",
                "passed": safety_non_inferior,
                "threshold": "Zero safety or warning sign regressions",
                "actual": "PASS" if safety_non_inferior else f"Regressions: {warning_regressions}",
            })
            if enforce_ab_significance:
                mcnemar_dir_pass = (
                    mcnemar_res["significant"]
                    and (mcnemar_res["contingency"]["candidate_better"] > mcnemar_res["contingency"]["baseline_better"])
                )
                wilcoxon_dir_pass = (
                    wilcoxon_res["significant"]
                    and (wilcoxon_res["mean_difference"] > 0.0)
                )
                gate_evaluations.extend([
                    {
                        "gate_name": "A_B_McNemar_Significance",
                        "passed": mcnemar_dir_pass,
                        "threshold": "p < 0.05 & candidate_better > baseline_better",
                        "actual": f"p={mcnemar_res['p_value']:.4f} ({mcnemar_res['contingency']['candidate_better']} vs {mcnemar_res['contingency']['baseline_better']})",
                    },
                    {
                        "gate_name": "A_B_Wilcoxon_Significance",
                        "passed": wilcoxon_dir_pass,
                        "threshold": "p < 0.05 & mean_mrr_diff > 0",
                        "actual": f"p={wilcoxon_res['p_value']:.4f} (diff={wilcoxon_res['mean_difference']:+.4f})",
                    },
                ])
            all_metric_gates_passed = all(g["passed"] for g in gate_evaluations)

    overall_status = "PASSED" if all_metric_gates_passed else "FAILED"

    report: Dict[str, Any] = {
        "status": overall_status,
        "scorecard_file": str(scorecard_file),
        "manifest_file": str(manifest_file),
        "benchmark_file": str(benchmark_file),
        "benchmark_sha256": actual_benchmark_sha256,
        "enforce_locked_certification": enforce_locked_certification,
        "baseline_mode": baseline_mode,
        "gates": gate_evaluations,
        "ab_comparison": ab_comparison,
    }

    return report


def main():
    parser = argparse.ArgumentParser(description="GuardDengue CI/CD Production Release Gate Validator")
    parser.add_argument("--scorecard", type=str, required=True, help="Path to evaluation scorecard JSON")
    parser.add_argument("--manifest", type=str, required=True, help="Path to release manifest JSON")
    parser.add_argument("--benchmark", type=str, required=True, help="Path to benchmark JSONL file")
    parser.add_argument("--baseline", type=str, default=None, help="Optional path to baseline scorecard JSON for A/B testing")
    parser.add_argument("--enforce-locked", action="store_true", help="Enforce Phase 3 cryptographic locked release certification")
    parser.add_argument("--baseline-mode", action="store_true", help="Validate safety/completeness/latency invariants without blocking on dense recall")
    parser.add_argument("--enforce-ab-significance", action="store_true", help="Require directional McNemar & Wilcoxon p < 0.05 on A/B comparison")
    parser.add_argument("--min-span-recall", type=float, default=0.90, help="Minimum acceptable Span Recall@5")
    parser.add_argument("--min-conjunct-recall", type=float, default=0.85, help="Minimum acceptable Conjunct Recall@5")
    parser.add_argument("--max-latency-p50", type=float, default=30.0, help="Maximum acceptable p50 latency in ms")
    args = parser.parse_args()

    try:
        report = validate_release_gates(
            eval_scorecard_path=args.scorecard,
            manifest_path=args.manifest,
            benchmark_dataset_path=args.benchmark,
            baseline_scorecard_path=args.baseline,
            enforce_locked_certification=args.enforce_locked,
            baseline_mode=args.baseline_mode,
            enforce_ab_significance=args.enforce_ab_significance,
            min_span_recall=args.min_span_recall,
            min_conjunct_recall=args.min_conjunct_recall,
            max_p50_latency_ms=args.max_latency_p50,
        )

        print("\n" + "=" * 75)
        print(" GuardDengue CI/CD Production Release Gate Report")
        print("=" * 75)
        print(f"Overall Status:        {report['status']}")
        print(f"Benchmark SHA-256:     {report['benchmark_sha256']}")
        print(f"Locked Certification:  {'ENFORCED' if report['enforce_locked_certification'] else 'OFF (Dev / Baseline Mode)'}")
        print("-" * 75)
        print("GATE EVALUATIONS:")
        for g in report["gates"]:
            status_str = "PASS" if g["passed"] else "FAIL"
            print(f"  [{status_str}] {g['gate_name']:<32} | Required: {str(g['threshold']):<28} | Actual: {g['actual']}")
        print("=" * 75)

        if report.get("ab_comparison"):
            ab = report["ab_comparison"]
            print("\nA/B HYPOTHESIS TESTING SUMMARY:")
            print(f"  Paired Cases:     {ab['paired_cases_count']}")
            print(f"  McNemar p-value:  {ab['mcnemar_test']['p_value']:.4f} (Significant: {ab['mcnemar_test']['significant']})")
            print(f"  Wilcoxon p-value: {ab['wilcoxon_test']['p_value']:.4f} (Significant: {ab['wilcoxon_test']['significant']})")
            print(f"  Mean MRR Diff:    {ab['wilcoxon_test']['mean_difference']:+.4f}")
            print(f"  Non-Inferiority:  {'PASSED' if ab['safety_non_inferior'] else 'FAILED'}")
            print("=" * 75)

        if report["status"] == "PASSED":
            print("\n[SUCCESS] All Release Gates Satisfied. Certified for Release.\n")
            sys.exit(0)
        else:
            print(f"\n[FAILURE] Release Gates Failed. Blocked from Deployment.\n", file=sys.stderr)
            sys.exit(1)

    except Exception as exc:
        print(f"[FATAL] Release gate validator encountered unhandled error: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
