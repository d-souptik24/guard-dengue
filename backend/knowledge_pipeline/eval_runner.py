"""
GuardDengue — Evaluation Runner & Dense Baseline Benchmark Suite (Phase 7)

Executes benchmark evaluations against the live RetrievalEngine and drug_registry
using the Canonical EvaluationAdapter. Measures span satisfaction, Reciprocal Rank (MRR@5),
deterministic semantic coverage, categorical medication safety, and local CPU latency.
Enforces strict release gates and outputs dense_baseline_scorecard.json.
"""

import json
import math
import time
import sqlite3
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Literal, Optional
import numpy as np

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.retrieval.adapter import create_evaluation_adapter, CanonicalEvaluationResult
from knowledge_pipeline.preflight import preflight_release_parity_check
from knowledge_pipeline.validate_benchmark import resolve_provenance_to_chunks


def score_retrieval_case(
    query_type: str,
    span_chunk_sets: List[set],
    retrieved_chunk_ids: List[str],
    top_k: int = 5,
) -> Dict[str, Optional[float]]:
    """
    Computes Span Recall@k, Conjunct Recall@k, and Reciprocal Rank (MRR@k)
    for a single evaluation case using chunking-invariant span satisfaction.
    """
    top_ids = retrieved_chunk_ids[:top_k]

    if query_type == "quarantined_coverage":
        return {
            "span_recall": None,
            "conjunct_recall": None,
            "mrr": None,
        }

    if not span_chunk_sets:
        raise ValueError(
            f"Non-quarantined query_type '{query_type}' must resolve at least 1 expected provenance span."
        )

    if query_type == "single_span":
        if len(span_chunk_sets) != 1:
            raise ValueError(
                f"single_span query expected exactly 1 span set, found {len(span_chunk_sets)}"
            )
        target_set = span_chunk_sets[0]
        hit = bool(target_set & set(top_ids))
        span_recall = 1.0 if hit else 0.0

        mrr = 0.0
        for rank, cid in enumerate(top_ids, start=1):
            if cid in target_set:
                mrr = 1.0 / rank
                break

        return {
            "span_recall": span_recall,
            "conjunct_recall": None,
            "mrr": mrr,
        }

    elif query_type == "conjunctive":
        if len(span_chunk_sets) < 2:
            raise ValueError(
                f"conjunctive query expected at least 2 span sets, found {len(span_chunk_sets)}"
            )
        span_hits = [bool(s & set(top_ids)) for s in span_chunk_sets]
        all_satisfied = all(span_hits)

        conjunct_recall = 1.0 if all_satisfied else 0.0
        span_recall = sum(span_hits) / len(span_chunk_sets)

        all_target_cids = set().union(*span_chunk_sets)
        mrr = 0.0
        for rank, cid in enumerate(top_ids, start=1):
            if cid in all_target_cids:
                mrr = 1.0 / rank
                break

        return {
            "span_recall": span_recall,
            "conjunct_recall": conjunct_recall,
            "mrr": mrr,
        }

    else:
        raise ValueError(f"Unsupported query_type '{query_type}' for retrieval scoring")


def run_evaluation(
    benchmark_path: Optional[Path | str] = None,
    corpus_release: str = "v0.1-dev",
    output_scorecard_path: Optional[Path | str] = None,
    top_k: int = 5,
    retrieval_mode: Literal["dense", "hybrid"] = "dense",
    enforce_retrieval_gate: bool = False,
) -> Dict[str, Any]:
    """
    Executes full deterministic evaluation suite across all benchmark cases.
    Fails closed if preflight parity fails or provenance cannot be resolved.
    """
    # 1. Step 1: Paginated Preflight Parity Check
    preflight_report = preflight_release_parity_check(expected_retrieval_mode=retrieval_mode)
    if preflight_report.get("status") != "PASSED":
        raise RuntimeError(f"Preflight release parity check failed: {preflight_report}")

    # 2. Step 2: Unrecorded warmup query to absorb ONNX Runtime / BM25 cold start
    create_evaluation_adapter(
        "warmup query cold start absorption",
        top_k=top_k,
        retrieval_mode=retrieval_mode,
    )

    # 3. Step 3: Load Benchmark Cases
    if benchmark_path is None:
        benchmark_path = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"
    benchmark_path = Path(benchmark_path)
    if not benchmark_path.exists():
        raise FileNotFoundError(f"Benchmark file not found at {benchmark_path}")

    cases = []
    with open(benchmark_path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.strip()
            if line_str:
                cases.append(json.loads(line_str))

    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    case_results: List[Dict[str, Any]] = []
    provenance_failures: List[Dict[str, Any]] = []

    try:
        for case in cases:
            eval_id = case["eval_id"]
            query = case["query"]
            query_type = case["query_type"]
            slice_name = case["slice"]
            exp_cov = case["expected_coverage"]
            exp_med = case["expected_medication"]

            # 3a. Dynamically resolve provenance anchors
            span_chunk_sets: List[set] = []
            for a_idx, prov in enumerate(case.get("expected_provenance", [])):
                matched_cids = resolve_provenance_to_chunks(
                    conn=conn,
                    doc_id=prov["doc_id"],
                    page_start=prov["page_start"],
                    page_end=prov["page_end"],
                    text_anchor=prov["key_text_anchor"],
                    section_path=prov.get("section_path"),
                )
                if not matched_cids:
                    provenance_failures.append({
                        "eval_id": eval_id,
                        "anchor_idx": a_idx,
                        "anchor": prov["key_text_anchor"],
                    })
                span_chunk_sets.append(set(matched_cids))

            # 3b. Execute Retrieval & Safety via Canonical Adapter
            t0 = time.perf_counter()
            adapter_res: CanonicalEvaluationResult = create_evaluation_adapter(
                query,
                top_k=top_k,
                retrieval_mode=retrieval_mode,
            )
            latency_ms = (time.perf_counter() - t0) * 1000.0

            retrieved_chunk_ids = adapter_res["retrieved_chunk_ids"]

            # 3c. Score Retrieval
            retrieval_scores = score_retrieval_case(
                query_type=query_type,
                span_chunk_sets=span_chunk_sets,
                retrieved_chunk_ids=retrieved_chunk_ids,
                top_k=top_k,
            )

            # 3d. Score Completeness & Semantic Coverage
            act_cov_status = adapter_res["coverage_status"]
            act_cov_reasons = adapter_res["coverage_reason_codes"]
            status_match = (act_cov_status == exp_cov["coverage_status"])
            reasons_match = (set(act_cov_reasons) == set(exp_cov["coverage_reason_codes"]))
            completeness_correct = (status_match and reasons_match)

            # 3e. Score Medication Safety
            act_med = adapter_res["medication_analysis"]
            med_is_expected_none = (exp_med["action_code"] == "STANDARD_EVIDENCE_RETRIEVAL" and not exp_med.get("detected_terms"))
            exp_terms = {t.lower() for t in exp_med.get("detected_terms", [])}

            if med_is_expected_none and act_med is None:
                action_code_match = True
                detected_terms_match = True
                ingredient_recall = 1.0
                ingredient_precision = 1.0
                negative_invariants_passed = True
                fail_closed = 1.0
            elif act_med is not None:
                action_code_match = (act_med["action_code"] == exp_med["action_code"])
                act_terms = {t.lower() for t in act_med.get("detected_terms", [])}
                detected_terms_match = (exp_terms == act_terms)

                exp_ings = set(exp_med.get("canonical_ingredients", []))
                act_ings = set(act_med.get("canonical_ingredients", []))

                if exp_ings:
                    inter = exp_ings & act_ings
                    ingredient_recall = len(inter) / len(exp_ings)
                    ingredient_precision = len(inter) / len(act_ings) if act_ings else 0.0
                else:
                    ingredient_recall = 1.0 if not act_ings else 0.0
                    ingredient_precision = 1.0 if not act_ings else 0.0

                negative_invariants_passed = (act_med["negative_invariants_passed"] == exp_med["negative_invariants_passed"])
                if exp_med["action_code"] == "ESCALATE_UNKNOWN_MEDICATION":
                    fail_closed = 1.0 if act_med["action_code"] == "ESCALATE_UNKNOWN_MEDICATION" else 0.0
                else:
                    fail_closed = 1.0
            else:
                action_code_match = False
                detected_terms_match = False
                ingredient_recall = 0.0
                ingredient_precision = 0.0
                negative_invariants_passed = False
                fail_closed = 0.0

            case_results.append({
                "eval_id": eval_id,
                "query": query,
                "query_type": query_type,
                "slice": slice_name,
                "latency_ms": latency_ms,
                "retrieved_chunk_ids": retrieved_chunk_ids,
                "span_recall": retrieval_scores["span_recall"],
                "conjunct_recall": retrieval_scores["conjunct_recall"],
                "mrr": retrieval_scores["mrr"],
                "coverage_status": act_cov_status,
                "expected_coverage_status": exp_cov["coverage_status"],
                "coverage_reason_codes": act_cov_reasons,
                "expected_coverage_reason_codes": exp_cov["coverage_reason_codes"],
                "completeness_correct": completeness_correct,
                "action_code": act_med["action_code"] if act_med else "STANDARD_EVIDENCE_RETRIEVAL",
                "expected_action_code": exp_med["action_code"],
                "action_code_match": action_code_match,
                "detected_terms": act_med.get("detected_terms", []) if act_med else [],
                "expected_detected_terms": exp_med.get("detected_terms", []),
                "detected_terms_match": detected_terms_match,
                "ingredient_recall": ingredient_recall,
                "ingredient_precision": ingredient_precision,
                "negative_invariants_passed": negative_invariants_passed,
                "fail_closed": fail_closed,
            })
    finally:
        conn.close()

    # 4. Step 4: Compute Aggregates & Cohort Breakdowns
    total_cases = len(case_results)
    latencies = [c["latency_ms"] for c in case_results]
    p50_latency = float(np.percentile(latencies, 50))
    p90_latency = float(np.percentile(latencies, 90))
    p95_latency = float(np.percentile(latencies, 95))
    mean_latency = float(np.mean(latencies))

    # Eligible retrieval cases (excluding quarantined_coverage where gold provenance is empty)
    eligible_retrieval_cases = [c for c in case_results if c["query_type"] != "quarantined_coverage"]
    span_recalls = [c["span_recall"] for c in eligible_retrieval_cases if c["span_recall"] is not None]
    mrrs = [c["mrr"] for c in eligible_retrieval_cases if c["mrr"] is not None]

    conjunctive_cases = [c for c in case_results if c["query_type"] == "conjunctive"]
    conjunct_recalls = [c["conjunct_recall"] for c in conjunctive_cases if c["conjunct_recall"] is not None]

    mean_span_recall = float(np.mean(span_recalls)) if span_recalls else 0.0
    mean_mrr = float(np.mean(mrrs)) if mrrs else 0.0
    mean_conjunct_recall = float(np.mean(conjunct_recalls)) if conjunct_recalls else 0.0

    # Per-slice retrieval metrics
    slice_breakdowns: Dict[str, Dict[str, Any]] = {}
    for sl in ["diagnostic_timing", "warning_signs_severe", "tables_flowcharts", "medication_safety", "quarantined_incomplete"]:
        sl_cases = [c for c in eligible_retrieval_cases if c["slice"] == sl]
        if sl_cases:
            sl_recalls = [c["span_recall"] for c in sl_cases if c["span_recall"] is not None]
            sl_mrrs = [c["mrr"] for c in sl_cases if c["mrr"] is not None]
            slice_breakdowns[sl] = {
                "case_count": len(sl_cases),
                "span_recall_at_5": float(np.mean(sl_recalls)) if sl_recalls else 0.0,
                "mrr_at_5": float(np.mean(sl_mrrs)) if sl_mrrs else 0.0,
            }
        else:
            slice_breakdowns[sl] = {"case_count": 0, "span_recall_at_5": 0.0, "mrr_at_5": 0.0}

    # Semantic coverage accuracy
    completeness_matches = [c["completeness_correct"] for c in case_results]
    completeness_flag_accuracy = float(np.mean(completeness_matches)) if completeness_matches else 0.0

    # Medication safety metrics (evaluated across medication_safety slice and any case expecting medication handling)
    med_slice_cases = [
        c for c in case_results
        if c["slice"] == "medication_safety" or c["expected_action_code"] != "STANDARD_EVIDENCE_RETRIEVAL" or c["expected_detected_terms"]
    ]
    ing_recalls = [c["ingredient_recall"] for c in med_slice_cases]
    ing_precisions = [c["ingredient_precision"] for c in med_slice_cases]
    inv_passes = [c["negative_invariants_passed"] for c in med_slice_cases]
    act_matches = [c["action_code_match"] for c in med_slice_cases]
    term_matches = [c["detected_terms_match"] for c in med_slice_cases]

    unknown_cases = [c for c in case_results if c["expected_action_code"] == "ESCALATE_UNKNOWN_MEDICATION"]
    fail_closed_rates = [c["fail_closed"] for c in unknown_cases]

    mean_ing_recall = float(np.mean(ing_recalls)) if ing_recalls else 1.0
    mean_ing_prec = float(np.mean(ing_precisions)) if ing_precisions else 1.0
    neg_inv_pass_rate = float(np.mean(inv_passes)) if inv_passes else 1.0
    action_code_accuracy = float(np.mean(act_matches)) if act_matches else 1.0
    detected_terms_accuracy = float(np.mean(term_matches)) if term_matches else 1.0
    fail_closed_rate = float(np.mean(fail_closed_rates)) if fail_closed_rates else 1.0

    # 5. Step 5: Enforce Release Gates via shared release_gates helper
    from knowledge_pipeline.release_gates import evaluate_scorecard_gates

    gate_evaluations = evaluate_scorecard_gates(
        provenance_failures=len(provenance_failures),
        ing_recall=mean_ing_recall,
        ing_precision=mean_ing_prec,
        fail_closed=fail_closed_rate,
        neg_invariants=neg_inv_pass_rate,
        completeness_acc=completeness_flag_accuracy,
        p50_latency=p50_latency,
        span_recall=mean_span_recall,
        conjunct_recall=mean_conjunct_recall,
        include_retrieval_gates=enforce_retrieval_gate,
    )
    all_gates_passed = all(g["passed"] for g in gate_evaluations)

    # 6. Step 6: Construct Final Scorecard Artifact
    scorecard: Dict[str, Any] = {
        "status": "PASSED" if all_gates_passed else "FAILED",
        "benchmark_file": str(benchmark_path),
        "corpus_release": corpus_release,
        "retrieval_mode": retrieval_mode,
        "retrieval_gates_enforced": enforce_retrieval_gate,
        "embedding_model": "BAAI/bge-small-en-v1.5",
        "total_cases": total_cases,
        "eligible_retrieval_cases": len(eligible_retrieval_cases),
        "provenance_resolution_failures": len(provenance_failures),
        "metrics": {
            "retrieval": {
                "span_recall_at_5": mean_span_recall,
                "conjunct_recall_at_5": mean_conjunct_recall,
                "mrr_at_5": mean_mrr,
                "slice_breakdown": slice_breakdowns,
            },
            "completeness": {
                "completeness_flag_accuracy": completeness_flag_accuracy,
            },
            "medication_safety": {
                "ingredient_recall": mean_ing_recall,
                "ingredient_precision": mean_ing_prec,
                "detected_terms_accuracy": detected_terms_accuracy,
                "negative_invariant_pass_rate": neg_inv_pass_rate,
                "action_code_accuracy": action_code_accuracy,
                "fail_closed_rate": fail_closed_rate,
            },
            "latency_ms": {
                "mean": mean_latency,
                "p50": p50_latency,
                "p90": p90_latency,
                "p95": p95_latency,
            },
        },
        "gates": gate_evaluations,
        "detailed_case_results": case_results,
    }

    if output_scorecard_path is None:
        default_filename = "dense_baseline_scorecard.json" if retrieval_mode == "dense" else "hybrid_rrf_scorecard.json"
        output_scorecard_path = settings.KNOWLEDGE_DIR / default_filename
    output_scorecard_path = Path(output_scorecard_path)
    output_scorecard_path.write_text(json.dumps(scorecard, indent=2), encoding="utf-8")

    return scorecard


def main():
    parser = argparse.ArgumentParser(description="GuardDengue Evaluation Runner & Benchmark Suite")
    parser.add_argument("--benchmark", type=str, default=None, help="Path to benchmark JSONL file")
    parser.add_argument("--release", type=str, default="v0.1-dev", help="Corpus release tag")
    parser.add_argument("--output", type=str, default=None, help="Output scorecard JSON path")
    parser.add_argument("--top-k", type=int, default=5, help="Top-K retrieval limit")
    parser.add_argument("--mode", type=str, choices=["dense", "hybrid"], default="dense", help="Retrieval mode")
    parser.add_argument("--enforce-retrieval-gate", action="store_true", help="Enforce Span_Recall@5 >= 0.90 and Conjunct_Recall@5 >= 0.85")
    args = parser.parse_args()

    try:
        scorecard = run_evaluation(
            benchmark_path=args.benchmark,
            corpus_release=args.release,
            output_scorecard_path=args.output,
            top_k=args.top_k,
            retrieval_mode=args.mode,
            enforce_retrieval_gate=args.enforce_retrieval_gate,
        )

        print("\n" + "=" * 70)
        print(f" GuardDengue Evaluation Scorecard ({scorecard['corpus_release']} | mode={scorecard['retrieval_mode']})")
        print("=" * 70)
        print(f"Overall Status: {scorecard['status']} (retrieval_gates_enforced={scorecard['retrieval_gates_enforced']})")
        print(f"Total Cases:    {scorecard['total_cases']}")
        print(f"Span_Recall@5:  {scorecard['metrics']['retrieval']['span_recall_at_5']:.4f}")
        print(f"Conjunct_Recall: {scorecard['metrics']['retrieval']['conjunct_recall_at_5']:.4f}")
        print(f"MRR@5:          {scorecard['metrics']['retrieval']['mrr_at_5']:.4f}")
        print(f"Completeness:   {scorecard['metrics']['completeness']['completeness_flag_accuracy']:.4f}")
        print(f"Ing_Recall:     {scorecard['metrics']['medication_safety']['ingredient_recall']:.4f}")
        print(f"Ing_Precision:  {scorecard['metrics']['medication_safety']['ingredient_precision']:.4f}")
        print(f"Det_Terms_Acc:  {scorecard['metrics']['medication_safety']['detected_terms_accuracy']:.4f}")
        print(f"Fail_Closed:    {scorecard['metrics']['medication_safety']['fail_closed_rate']:.4f}")
        print(f"Neg_Invariants: {scorecard['metrics']['medication_safety']['negative_invariant_pass_rate']:.4f}")
        print(f"p50 Latency:    {scorecard['metrics']['latency_ms']['p50']:.2f} ms")
        print(f"p95 Latency:    {scorecard['metrics']['latency_ms']['p95']:.2f} ms")
        print("-" * 70)
        print("RELEASE GATES:")
        for g in scorecard["gates"]:
            status_str = "PASS" if g["passed"] else "FAIL"
            print(f"  [{status_str}] {g['gate_name']:<32} | Required: {str(g['threshold']):<10} | Actual: {g['actual']}")
        print("=" * 70)

        if scorecard["status"] == "PASSED":
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as exc:
        print(f"[FATAL] Evaluation runner failed: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
