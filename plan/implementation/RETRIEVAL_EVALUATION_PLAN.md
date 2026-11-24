# GuardDengue: Retrieval Quality, Medication Safety, and Release-Gating Implementation Paper

**Authors:** Souptik Dutta & Ayan Chakraborty  
**Corpus Release:** `v0.1-dev` (`425` approved WHO chunks; `189` quarantined NCVBDC chunks; `3` pending figures)  
**Runtime Default:** `RETRIEVAL_MODE = "dense"` (`Phase 8A` Hybrid RRF implemented & evaluated; `Phases 1–8B` verified; `Phase 8C` queued)

---

## Abstract

Clinical retrieval-augmented generation (RAG) fails in two quiet ways: retrieval misses get masked by loose evaluation, and drug-safety guardrails break on regional brand combinations. This document records the end-to-end engineering, mathematical formulation, and experimental evaluation behind GuardDengue's retrieval and medication-safety pipeline across **Phases 1 through 8B**, along with the remaining **Phase 8C** certification protocol.

After fixing stale database paths, building a deterministic semantic-coverage matrix, decomposing Indian fixed-dose drug combinations, and enforcing paginated SQLite-to-Qdrant parity, an initial Phase 7 dense baseline (`0.9310` recall) turned out to be inflated by post-hoc query edits. Reverting those edits in **Phase 7R** exposed the real dense baseline on `eval_dev_smoke.jsonl` (`0.5345` `Span_Recall@5`, `0.3891` `MRR@5`). In **Phase 8A**, integrating FastEmbed `Qdrant/bm25` sparse retrieval with `BAAI/bge-small-en-v1.5` via Reciprocal Rank Fusion (`Fusion.RRF`), calibrated on a disjoint 35-case split (`eval_dev_calib.jsonl`) with an out-of-scope dense cosine floor ($\tau_{\text{oos}} = 0.67$), lifted frozen 50-case validation `Span_Recall@5` from `0.8878` to **`0.9592`** and `MRR@5` from `0.7585` to **`0.8289`** (Wilcoxon $p = 0.0199$, zero safety regressions, `p50 = 28.90 ms`). However, single-query RRF still missed `Conjunct_Recall@5 >= 0.85` (`0.6000`) and binary McNemar significance ($p = 0.1250$, `4 vs 0` discordant pairs). A prototyped two-clause query splitter broke non-inferiority (`VAL_021` regression) and was rejected. Consequently, **Phase 8B** consolidated gate evaluation and added hybrid preflight tests (`105/105` pytest passing), while keeping `RETRIEVAL_MODE = "dense"` until **Phase 8C** locked dual-clinician holdout certification.

### Contents
1. [Thought Process: Before Planning vs. After Codebase Review](#1-thought-process-before-planning-vs-after-codebase-review)
2. [Changed & Added Workspace Structure](#2-changed--added-workspace-structure)
3. [Mathematical Problem Specification](#3-mathematical-problem-specification)
4. [Phase-by-Phase Engineering Walkthrough (Phases 1 to 8B)](#4-phase-by-phase-engineering-walkthrough-phases-1-to-8b)
5. [Pending Future Work: Phase 8C (Dual-Clinician Locked Production Certification)](#5-pending-future-work-phase-8c-dual-clinician-locked-production-certification)
6. [Master Verification Ledger](#6-master-verification-ledger)

---

## 1. Thought Process: Before Planning vs. After Codebase Review

Before touching any code, the goal looked straightforward: measure how well GuardDengue retrieves WHO dengue guidelines, verify that NSAIDs are blocked, and compare dense vectors against hybrid search.

Reading the actual repository changed that plan immediately. Four concrete gaps showed up in the existing code:

1. **Stale Default Database Path:** `backend/app/core/config.py` pointed `SQLITE_DB_PATH` to `backend/data/guarddengue_chunks.db` (a 69 KB mock file with zero rows), whereas the real 3.2 MB SQLite database (`617` total chunks: `425` approved, `189` quarantined NCVBDC chunks, `3` pending figures) and Qdrant store (`guarddengue_v0.1-dev`) lived under `backend/knowledge_pipeline/extracted/`. Any evaluation run reading default settings would have measured an empty store.
2. **Dual Vectors Already Indexed:** Qdrant `guarddengue_v0.1-dev` already stored both `"dense"` (`BAAI/bge-small-en-v1.5`, 384-d cosine) and `"sparse"` (`Qdrant/bm25` IDF) vectors for all 425 active points, yet runtime search queried `"dense"` only.
3. **Broken Coverage Heuristic:** `RetrievalEngine.retrieve()` marked coverage `"complete"` whenever `len(chunks) >= 2`, regardless of whether the user asked for an Indian NCVBDC protocol (quarantined), a pending figure, or an unconfirmed jurisdiction.
4. **Early-Return Drug Screening Bug:** `backend/app/safety/drug_registry.py` matched only an 8-NSAID regex list. Fixed-dose combinations like `Combiflam` (ibuprofen + paracetamol) or `Zerodol-P` (aceclofenac + paracetamol) either slipped through or hid constituent NSAIDs, while unknown drug names had no fail-closed escalation path.

Those four findings forced a strict bottom-up order: **synchronize stores first (Phase 1), freeze evaluation contracts (Phase 2), fix safety and coverage logic (Phases 3–4), prove SQLite-to-Qdrant parity (Phase 5), ground benchmarks in document spans instead of chunk UUIDs (Phase 6), establish an honest dense baseline (Phases 7–7R), and only then run a leakage-free Hybrid A/B experiment (Phases 8A–8B).**

```mermaid
flowchart LR
    Q["User / Benchmark Query"] --> Z2["Zone 2: Unsplit Safety & Scope"]
    Z2 -->|"Urgent Red-Flag"| U["Urgent 108 Override"]
    Z2 -->|"NSAID / FDC / Unknown"| M["Deterministic Med Template"]
    Z2 -->|"Informational"| Z4["Zone 4: RetrievalEngine"]
    Z4 -->|"mode = dense"| VD["Qdrant Dense Cosine"]
    Z4 -->|"mode = hybrid"| VH["Dense + BM25 RRF + OOS Floor (0.67)"]
    VD --> COV["6-Row Coverage Matrix"]
    VH --> COV
    COV --> AD["CanonicalEvaluationResult"]
    AD --> RG["Release Gates & Statistical A/B"]
```

---

## 2. Changed & Added Workspace Structure

Only files created or modified across Phases 1 through 8B are listed below (derived directly from `git status --short`):

```text
guard-dengue/
├── plan/
│   └── implementation/
│       └── RETRIEVAL_EVALUATION_PLAN.md          # Master implementation & evaluation paper
└── backend/
    ├── app/
    │   ├── core/
    │   │   └── config.py                         # Extracted store paths, RETRIEVAL_MODE, OOS floor (0.67)
    │   ├── retrieval/
    │   │   ├── adapter.py                        # CanonicalEvaluationResult, RequestedScope bridge
    │   │   ├── embeddings.py                     # Fail-closed Qdrant/bm25 sparse embedder + dense cache
    │   │   ├── engine.py                         # 6-row coverage matrix, parent-skip, _enrich_hybrid_clause
    │   │   ├── policy_store.py                   # Safety policy lookup integration
    │   │   ├── sqlite_store.py                   # Approved chunk & manifest queries
    │   │   └── vector_store.py                   # Dense + Hybrid Prefetch/RRF + OOS cosine gate
    │   └── safety/
    │       └── drug_registry.py                  # 9 NSAIDs, 8 Indian FDCs, chronic/negated/unknown rules
    ├── knowledge_pipeline/
    │   ├── __init__.py
    │   ├── build_smoke_benchmark.py              # Reproducible builder for 30-case smoke set
    │   ├── validate_benchmark.py                 # 5-20 token anchor & SQLite provenance resolver
    │   ├── preflight.py                          # Paginated SQLite <-> Qdrant & sparse-vector audit
    │   ├── eval_runner.py                        # Evaluation runner calling shared gate evaluator
    │   ├── release_gates.py                      # Shared gate evaluator, McNemar, Wilcoxon, SHA-256 lock
    │   └── extracted/
    │       ├── release_manifest_v0.1-dev.json    # Corpus & safety policy manifest
    │       ├── eval_dev_smoke.jsonl              # 30 smoke cases (29 retrieval-eligible)
    │       ├── eval_dev_calib.jsonl              # 35 disjoint calibration cases (25 clinical + 10 OOS)
    │       ├── eval_dev_validation.jsonl         # 50 frozen held-out validation cases (10 conjunctive)
    │       ├── dense_baseline_scorecard.json     # Untainted Phase 7R dense smoke scorecard
    │       ├── dense_validation_scorecard.json   # Dense baseline on frozen 50-case validation set
    │       └── hybrid_rrf_scorecard.json         # Hybrid BM25+RRF candidate on frozen 50-case set
    └── tests/
        ├── verify_phase1.py                      # Phase 1 store & manifest verification
        ├── test_adapter_contracts.py             # Phase 2 schema & serialization checks
        ├── test_semantic_coverage.py             # Phase 3 6-row coverage matrix tests
        ├── test_medication_safety_registry.py    # Phase 4 FDC, chronic, negated, unknown drug tests
        ├── test_preflight_parity.py              # Phase 5 + 8B dense & hybrid preflight tests
        ├── test_validate_benchmark.py            # Phase 6 schema & provenance validation tests
        ├── test_eval_runner.py                   # Phase 7 scorer & runner invariants
        ├── test_hybrid_retrieval.py              # Phase 8A BM25 fail-closed, RRF rescue & OOS tests
        ├── test_release_gates.py                 # Phase 8A/8B McNemar, Wilcoxon & locked gate tests
        └── test_retrieval.py                     # Core Zone 4 retrieval integration tests
```

---

## 3. Mathematical Problem Specification

Every metric and statistical test below comes directly from [eval_runner.py](guard-dengue/backend/knowledge_pipeline/eval_runner.py), [vector_store.py](guard-dengue/backend/app/retrieval/vector_store.py), and [release_gates.py](guard-dengue/backend/knowledge_pipeline/release_gates.py).

### 3.1 Chunking-Invariant Provenance & Retrieval Metrics

Let $Q_{\text{elig}}$ be the set of evaluation queries with `query_type != "quarantined_coverage"`. Each query $q \in Q_{\text{elig}}$ defines $m_q \ge 1$ expected provenance anchors $\{a_1, \dots, a_{m_q}\}$. Each anchor $a_j$ resolves dynamically against approved SQLite child chunks into a non-empty target chunk-ID set $S_{q,j} \subseteq \mathcal{C}_{\text{approved}}$. Let $R_k(q) = (c_1, \dots, c_k)$ be the ordered top-$k$ chunk IDs returned by the retriever ($k = 5$ in all Phase 7–8 runs).

An anchor $a_j$ is satisfied if any matching chunk appears in the top-$k$ list:

$$h_{q,j} = \mathbb{I}\!\left[ R_k(q) \cap S_{q,j} \neq \emptyset \right]$$

For query $q$, per-query span recall is the fraction of its required anchors satisfied, and conjunctive satisfaction requires **all** spans simultaneously:

$$\text{SpanRecall}_k(q) = \frac{1}{m_q} \sum_{j=1}^{m_q} h_{q,j}, \qquad \text{ConjunctHit}_k(q) = \prod_{j=1}^{m_q} h_{q,j}$$

Dataset-level `Span_Recall@5` averages $\text{SpanRecall}_5(q)$ over $q \in Q_{\text{elig}}$, while `Conjunct_Recall@5` averages $\text{ConjunctHit}_5(q)$ over multi-span queries ($m_q \ge 2$).

Reciprocal rank uses the earliest top-$k$ rank matching **any** expected span set $S_q = \bigcup_{j=1}^{m_q} S_{q,j}$:

$$\text{RR}_k(q) = \begin{cases} \dfrac{1}{\min \{ r \in \{1,\dots,k\} : c_r \in S_q \}} & \text{if } R_k(q) \cap S_q \neq \emptyset, \\ 0 & \text{otherwise.} \end{cases}$$

Dataset `MRR@5` is the mean of $\text{RR}_5(q)$ across $q \in Q_{\text{elig}}$.

### 3.2 Hybrid Reciprocal Rank Fusion & Dense OOS Abstention Gate

In `hybrid` mode, Qdrant executes two filtered candidate prefetches with limit $L = \text{HYBRID\_PREFETCH\_LIMIT} = 20$: a 384-d dense cosine prefetch and a `Qdrant/bm25` sparse prefetch. Qdrant's `Fusion.RRF` ranks candidate $d$ by fused rank score:

$$\text{RRF}(d) = \sum_{m \in \{\text{dense}, \text{sparse}\}} \frac{1}{\kappa + \text{rank}_m(d)}$$

Because RRF scores depend only on rank (typically $0.33$ to $0.83$ rather than cosine similarity), applying a cosine cutoff like $0.60$ directly to $\text{RRF}(d)$ would drop legitimate rank 2–5 hits. Instead, `VectorStore.search()` fetches `"dense"` vectors on the top-$k$ fused candidates and checks the maximum exact dot product against the calibrated out-of-scope floor $\tau_{\text{oos}} = 0.67$:

$$\text{Hits}_{\text{hybrid}}(q) = \begin{cases} \emptyset & \text{if } \max_{d \in \text{Top-}k} \langle \mathbf{q}_{\text{dense}}, \mathbf{d}_{\text{dense}} \rangle < \tau_{\text{oos}}, \\ \text{Top-}k & \text{otherwise.} \end{cases}$$

When $\text{Hits}_{\text{hybrid}}(q) = \emptyset$, `RetrievalEngine.retrieve()` abstains with `coverage_status = "unavailable"` and reason code `NO_APPROVED_EVIDENCE`.

### 3.3 Paired Statistical Hypothesis Tests

For paired A/B testing on $N_{\text{pair}}$ eligible queries shared between baseline $B$ and candidate $C$:

1. **McNemar's Paired Test (Binary Span Satisfaction):** Define binary pass $y_q = \mathbb{I}[\text{SpanRecall}_5(q) \ge 1.0]$. Let $b = \sum_q \mathbb{I}[\neg y_q^B \land y_q^C]$ (candidate wins) and $c = \sum_q \mathbb{I}[y_q^B \land \neg y_q^C]$ (baseline wins), with discordant count $n_d = b + c$.
   * When $n_d < 25$, `release_gates.py` runs an exact two-sided binomial test under $H_0: p = 0.5$:
     $$p_{\text{McNemar}} = 2 \sum_{i=\max(b,c)}^{n_d} \binom{n_d}{i} 0.5^{n_d} \quad (\text{capped at } 1.0).$$
   * When $n_d \ge 25$, it uses Edwards continuity-corrected $\chi^2$:
     $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \qquad df = 1.$$
2. **Wilcoxon Signed-Rank Test (Continuous `MRR@5`):** Paired differences $\Delta_q = \text{RR}_5^C(q) - \text{RR}_5^B(q)$ are tested via `scipy.stats.wilcoxon(cand, base)` (returning $p = 1.0$ if all $\Delta_q = 0$). Significance requires $p < 0.05$ and positive directional gain ($b > c$ for McNemar; $\bar{\Delta} > 0$ for Wilcoxon).

### 3.4 Cryptographic Integrity & Hard Release Constraints

For a locked benchmark file $F$, SHA-256 verification checks $H(F) = \text{SHA-256}(\text{bytes}(F))$ against `locked_benchmark_sha256`. Release certification enforces:
* `Provenance_Resolution_Failures == 0`
* `Ingredient_Recall == 1.00`, `Ingredient_Precision == 1.00`, `Fail_Closed_Rate == 1.00`, `Negative_Invariant_Pass_Rate == 1.00`, `Completeness_Flag_Accuracy == 1.00` (within $|\hat{v} - 1.0| \le 10^{-5}$)
* `Latency_p50_ms < 30.0 ms`, `Span_Recall@5 >= 0.90`, `Conjunct_Recall@5 >= 0.85`
* `A_B_Non_Inferiority`: zero case-level regressions on `warning_signs_severe` or any medication safety metric.

---

## 4. Phase-by-Phase Engineering Walkthrough (Phases 1 to 8B)

### Phase 1: Environment, Store & Config Synchronization

* **Why this decision:** Default config pointed `SQLITE_DB_PATH` to an empty mock database while extracted WHO/NCVBDC assets sat in `backend/knowledge_pipeline/extracted/`. No downstream evaluation means anything if paths are wrong.
* **Benefits:** Guarantees every script—from preflight checks to benchmark scoring—reads the exact same SQLite database, Qdrant collection, and embedding model without silent path drift.
* **Trade-offs:** Pinning `CORPUS_RELEASE = "v0.1-dev"` and `QDRANT_COLLECTION = "guarddengue_v0.1-dev"` in [config.py](guard-dengue/backend/app/core/config.py) eliminates silent fallbacks to mock data, at the cost of requiring a manifest bump when `v0.2` is ingested.
* **Implementation:** Pointed `SQLITE_DB_PATH` and `QDRANT_STORAGE_DIR` to `extracted/`, updated [sqlite_store.py](guard-dengue/backend/app/retrieval/sqlite_store.py) queries to match the extracted `parent_chunks` and `child_chunks` schema (`artifact_ref`, `chunk_content_hash`, `metadata_json`, `superseded_by`), flipped `USE_FASTEMBED` default from `"0"` to `"1"` in [embeddings.py](guard-dengue/backend/app/retrieval/embeddings.py) so `BAAI/bge-small-en-v1.5` runs instead of mock hashing, and created [release_manifest_v0.1-dev.json](guard-dengue/backend/knowledge_pipeline/extracted/release_manifest_v0.1-dev.json) binding corpus release, collection name, embedding model, and safety policy hash.
  ```python
  # guard-dengue/backend/app/core/config.py
  KNOWLEDGE_DIR: Path = BACKEND_ROOT / "knowledge_pipeline" / "extracted"
  SQLITE_DB_PATH: Path = (
      KNOWLEDGE_DIR / "guarddengue_chunks.db"
      if (KNOWLEDGE_DIR / "guarddengue_chunks.db").exists()
      else DATA_DIR / "guarddengue_chunks.db"
  )
  QDRANT_COLLECTION: str = "guarddengue_v0.1-dev"
  RETRIEVAL_MODE: Literal["dense", "hybrid"] = "dense"
  HYBRID_PREFETCH_LIMIT: int = 20
  HYBRID_DENSE_OOS_FLOOR: float = 0.67
  ```
* **Outcome:** Verified via [verify_phase1.py](guard-dengue/backend/tests/verify_phase1.py): `425` approved chunks and manifest JSON confirmed on disk.

### Phase 2: Canonical Evaluation Adapter & Data Contracts

* **Why this decision:** `RetrievalEngine.retrieve()` originally returned raw internal objects or a 4-tuple, coupling evaluation scripts to runtime internals.
* **Benefits:** Decouples evaluation tooling from `RetrievalEngine` internals so both dense and hybrid pipelines emit the exact same JSON-serializable schema for A/B comparison and audit logging.
* **Trade-offs:** Adding [adapter.py](guard-dengue/backend/app/retrieval/adapter.py) introduces one lightweight mapping layer (`~2–3 ms` including medication analysis and manifest metadata), in exchange for a strict JSON-serializable `CanonicalEvaluationResult` (`CONTRACT_VERSION = "1.0.0"`) across dense and hybrid runs.
* **Implementation:** Defined `RequestedScope`, `MedicationAnalysis`, and `CanonicalEvaluationResult` TypedDicts in `adapter.py`, bridged via `create_evaluation_adapter(query, top_k=5, retrieval_mode="dense", collection_name=None)`. `latency_ms` is timed inside `RetrievalEngine.retrieve()` via `time.perf_counter()` (embedding + Qdrant search + coverage matrix) and paired with manifest/safety policy hashes for audit reproducibility.
  ```python
  # guard-dengue/backend/app/retrieval/adapter.py
  class CanonicalEvaluationResult(TypedDict):
      contract_version: str
      retrieved_chunk_ids: list[str]
      coverage_status: Literal["complete", "partial", "unavailable"]
      coverage_reason_codes: list[str]
      requested_scope: RequestedScope
      jurisdiction_coverage: dict[str, str]
      medication_analysis: MedicationAnalysis | None
      retrieval_mode: Literal["dense", "hybrid"]
      release_manifest_hash: str
      latency_ms: float
  ```
* **Outcome:** All `8` tests in [test_adapter_contracts.py](guard-dengue/backend/tests/test_adapter_contracts.py) pass.

### Phase 3: Semantic Coverage Engine & `RetrievalEngine` Upgrade

* **Why this decision:** A count heuristic (`len(chunks) >= 2 -> "complete"`) cannot distinguish WHO global guidance from an unavailable Indian NCVBDC protocol or a pending figure.
* **Benefits:** Prevents unsafe over-claiming by separating evidence completeness from chunk count—explicitly flagging missing local Indian protocols, unconfirmed jurisdictions, and pending clinical figures while keeping emergency escalation independent.
* **Trade-offs:** Deterministic query-text rules (`_determine_requested_scope` and `has_explicit_ncvbdc_demand`) are fast and predictable, though they rely on explicit geography/protocol terms rather than LLM intent parsing. Importantly, because the `189` NCVBDC chunks are quarantined out of Qdrant, Row 2 *must* trigger from query demand rather than Qdrant chunk metadata.
* **Implementation:** Built the 6-row coverage decision matrix in [engine.py](guard-dengue/backend/app/retrieval/engine.py) (Row 1 `complete`, Row 2 `unavailable` on explicit `NCVBDC`/`NVBDCP`, Row 3 `partial` on generic India queries, Row 4 `partial` on unstated geography, Row 5 `partial` on pending figures, Row 6 decoupled urgency).
  ```python
  # guard-dengue/backend/app/retrieval/engine.py
  if len(evidence_chunks) == 0:
      evidence_ok = False
      coverage_status = "unavailable"
      if has_explicit_ncvbdc_demand or requested_scope["requires_local_protocol"]:
          reason_codes = ["EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE"]
      else:
          reason_codes = ["NO_APPROVED_EVIDENCE"]
  elif has_explicit_ncvbdc_demand:
      # Explicit national protocol requested, but NCVBDC is quarantined; only global WHO returned
      coverage_status = "unavailable"
      reason_codes = ["EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE"]
      evidence_ok = False
  ```
* **Outcome:** All `8` tests in [test_semantic_coverage.py](guard-dengue/backend/tests/test_semantic_coverage.py) pass.

### Phase 4: Categorical Medication Safety Registry Upgrade

* **Why this decision:** Indian patients rarely type `"ibuprofen"` or `"aceclofenac"`—they type `"Combiflam"`, `"Flexon"`, `"Zerodol-P"`, or `"Meftal-Spas"`. An early-return 8-NSAID regex missed FDCs and masked safe/chronic edge cases.
* **Benefits:** Catches dangerous hidden NSAIDs inside Indian fixed-dose combinations before retrieval or generation, while avoiding false alarms on negated questions ("should I avoid ibuprofen?") and escalating chronic antiplatelet prescriptions to clinicians.
* **Trade-offs:** Rule-based constituent decomposition in [drug_registry.py](guard-dengue/backend/app/safety/drug_registry.py) guarantees `100%` deterministic recall on cataloged Indian FDCs and chronic antiplatelets, while requiring explicit dictionary maintenance for new market brands.
* **Implementation:** Expanded `NSAID_DATABASE` to `9` NSAIDs (including `aceclofenac`, bilingual English/Bengali aliases), curated an `8`-entry `INDIAN_FDC_DATABASE`, implemented `analyze_medication_query()` returning `7` action codes, and updated `lookup_drug_policy()` in [policy_store.py](guard-dengue/backend/app/retrieval/policy_store.py) to expand brand names and FDC constituents (`nsaid_constituent` + `constituents`) into `search_names` before matching `safety_policy_v0.1-dev.json` rules.
  ```python
  # guard-dengue/backend/app/safety/drug_registry.py
  if re.search(pattern, clean_text, re.IGNORECASE) or alias in query:
      if has_negation:
          action_code = "NEGATED_MENTION_EDUCATION"
          template_id = "TMPL_NEGATED_NSAID_EDU_V1"
      elif is_chronic:
          action_code = "CHRONIC_PRESCRIPTION_ESCALATE"
          template_id = "TMPL_CHRONIC_RX_SAFETY_V1"
      else:
          action_code = "AVOID_FDC_CONTRAINDICATED"
          template_id = "TMPL_FDC_AVOID_V1"
      policy_statuses = {c: "contraindicated" if c != "paracetamol" else "safe" for c in fdc["constituents"]}
  ```
* **Outcome:** All `13` tests in [test_medication_safety_registry.py](guard-dengue/backend/tests/test_medication_safety_registry.py) pass with `1.00` `Fail_Closed_Rate` and `1.00` `Negative_Invariant_Pass_Rate`.

### Phase 5: Paginated Preflight Parity Suite

* **Why this decision:** If SQLite and Qdrant drift—or if a single quarantined NCVBDC chunk leaks into Qdrant—evaluation scores become meaningless or unsafe.
* **Benefits:** Acts as a hard pre-evaluation circuit breaker: confirms exact `1:1` content-hash parity between SQLite and Qdrant, zero quarantined leakage, and valid dense/sparse vectors in hybrid collections before any benchmark runs.
* **Trade-offs:** Scrolling all `425` Qdrant points before evaluation adds a one-time startup check, completely eliminating silent corpus drift.
* **Implementation:** Built [preflight.py](guard-dengue/backend/knowledge_pipeline/preflight.py) with paginated scrolling, exact `SQLite == Qdrant` ID-set equality, `chunk_content_hash` verification, quarantine exclusion (`unapproved_ids` intersection empty), manifest SHA-256 verification, and hybrid sparse-vector checks.
  ```python
  # guard-dengue/backend/knowledge_pipeline/preflight.py
  require_sparse = (expected_retrieval_mode == "hybrid")
  if require_sparse:
      coll_info = client.get_collection(collection_name)
      sparse_cfg = getattr(coll_info.config.params, "sparse_vectors", None) or {}
      if "sparse" not in sparse_cfg:
          raise AssertionError(f"Collection '{collection_name}' lacks required 'sparse' vector config for hybrid mode.")
  # Inside paginated client.scroll(..., with_vectors=require_sparse):
  if require_sparse:
      vec_map = r.vector if isinstance(r.vector, dict) else {}
      if not vec_map.get("dense") or not vec_map.get("sparse") or not getattr(vec_map.get("sparse"), "indices", None):
          raise AssertionError(f"Qdrant point {chunk_id} is missing non-empty 'dense' or 'sparse' named vector.")
  ```
* **Outcome:** `[SUCCESS] Preflight Parity Passed: 425 chunks verified in sync`.

### Phase 6: Authoring Developer Smoke Benchmark (`eval_dev_smoke.jsonl`)

* **Why this decision:** Evaluating against static chunk UUIDs breaks whenever PDF chunking changes. Grounding each test case in `5–20` token verbatim text spans resolved dynamically against SQLite makes ground truth chunking-invariant.
* **Benefits:** Keeps benchmark ground truth valid across re-chunking or index rebuilds, and rejects stale, quarantined, or over-broad anchors automatically at validation time.
* **Trade-offs:** Writing and verifying verbatim anchors takes upfront tooling ([build_smoke_benchmark.py](guard-dengue/backend/knowledge_pipeline/build_smoke_benchmark.py)), but eliminates brittle UUID maintenance.
* **Implementation:** Authored `30` cases across `5` slices (`diagnostic_timing`: 6, `warning_signs_severe`: 8, `tables_flowcharts`: 4, `medication_safety`: 8, `quarantined_incomplete`: 4) in [eval_dev_smoke.jsonl](guard-dengue/backend/knowledge_pipeline/extracted/eval_dev_smoke.jsonl) and enforced schema/token bounds in [validate_benchmark.py](guard-dengue/backend/knowledge_pipeline/validate_benchmark.py).
  ```python
  # guard-dengue/backend/knowledge_pipeline/validate_benchmark.py
  cur.execute(
      "SELECT chunk_id, text, section_path FROM child_chunks "
      "WHERE doc_id = ? AND page_start <= ? AND page_end >= ? "
      "AND review_status = 'approved' AND superseded_by IS NULL",
      (doc_id, page_end, page_start),
  )
  norm_anchor = normalize_whitespace(text_anchor).lower()
  matching_chunk_ids = [
      chunk_id for chunk_id, chunk_text, _ in cur.fetchall()
      if norm_anchor in normalize_whitespace(chunk_text).lower()
  ]
  ```
* **Outcome:** `30 cases validated, 0 provenance resolution failures`; all `7` tests in [test_validate_benchmark.py](guard-dengue/backend/tests/test_validate_benchmark.py) pass.

### Phase 7 & Phase 7R: Dense Baseline, Taint Audit, and Remediation

* **Why this decision:** The first Phase 7 dense run reported `0.9310` `Span_Recall@5`, which looked suspiciously high for dense-only retrieval. Auditing the diff revealed `15` cases in `eval_dev_smoke.jsonl` whose queries or anchors had been altered after probing dense retrieval misses (`Category B` tampering), alongside `3` legitimate schema/registry bugs (`Category A`).
* **Benefits:** Restored scientific integrity to the baseline measurement and exposed the real lexical recall gap (`0.5345` `Span_Recall@5`, `0.0000` `Conjunct_Recall@5`) that Hybrid RRF needed to solve.
* **Trade-offs:** Reverting all `15` Category B query/anchor edits dropped headline smoke `Span_Recall@5` from `0.9310` down to `0.5345`, which felt painful—but kept the baseline honest and prevented circular evaluation.
* **Implementation:** Restored original Phase 6 queries/anchors via `build_smoke_benchmark.py`, fixed only the `Category A` coverage/registry misalignments (`SMOKE_022`, `expected_coverage` on WHO/India cases), separated `--baseline-mode` from strict promotion in `release_gates.py`, and implemented `single_span` and `conjunctive` scoring in `eval_runner.py`.
  ```python
  # guard-dengue/backend/knowledge_pipeline/eval_runner.py
  elif query_type == "conjunctive":
      span_hits = [bool(s & set(top_ids)) for s in span_chunk_sets]
      conjunct_recall = 1.0 if all(span_hits) else 0.0
      span_recall = sum(span_hits) / len(span_chunk_sets)
      all_target_cids = set().union(*span_chunk_sets)
      mrr = next((1.0 / rank for rank, cid in enumerate(top_ids, start=1) if cid in all_target_cids), 0.0)
  ```
* **Outcome:** Recorded untainted [dense_baseline_scorecard.json](guard-dengue/backend/knowledge_pipeline/extracted/dense_baseline_scorecard.json): `Span_Recall@5 = 0.5345`, `Conjunct_Recall@5 = 0.0000`, `MRR@5 = 0.3891`, `Completeness = 1.00`, `Medication Safety = 1.00`, `p50 = 19.18 ms`.

### Phase 8A: Hybrid BM25 + Dense RRF & Controlled A/B Experiment

```mermaid
flowchart TD
    Q["Original Query"] --> Z2["Zone 2: _determine_requested_scope & analyze_medication_query"]
    Q --> EN["Zone 4: _enrich_hybrid_clause (unmasked NSAID brands only)"]
    EN --> DE["Dense Embed (bge-small-en-v1.5, ~6.0 ms)"]
    EN --> SP["Sparse Embed (Qdrant/bm25, ~0.1 ms, fail-closed)"]
    DE --> PF["Dual Prefetch (limit = 20 each) + Fusion.RRF"]
    SP --> PF
    PF --> OOS{"max(dense_cos) >= 0.67?"}
    OOS -->|"No (OOS / Stopword Collision)"| EMPTY["Return [] -> NO_APPROVED_EVIDENCE"]
    OOS -->|"Yes"| HITS["Return Top-k Fused Chunks (p50 = 28.90 ms)"]
```

* **Why this decision:** Dense vectors alone missed exact clinical acronyms (`EDTA`, `RT-PCR`, table titles) and unmasked Indian NSAID brands (`Brufen`, `Combiflam`, `Voveran`) not printed in WHO PDFs. Meanwhile, evaluating improvements on the `30`-case smoke set risked circular overfitting.
* **Benefits:** Captures exact clinical terms and Indian drug brands via `Qdrant/bm25` fused with `bge-small-en-v1.5` (`Span_Recall@5` jumped `+7.14 pp` to `0.9592` and `MRR@5` improved significantly at Wilcoxon $p = 0.0199$), while blocking out-of-scope BM25 stopword collisions via the calibrated dense cosine floor (`0.67`) within the `< 30 ms` CPU budget (`p50 = 28.90 ms`).
* **Trade-offs:**
  * *OOS Floor Calibration:* Spurious single-word BM25 matches (e.g., PostgreSQL `"tables"` matching WHO clinical tables at cosine `0.6643`) leaked at $\tau_{\text{oos}} = 0.60$. Calibrating strictly on **disjoint `eval_dev_calib.jsonl` (`25` clinical + `10` OOS = `35` cases)** found OOS max `0.6643` vs. calibration clinical min `0.7665`, locking `HYBRID_DENSE_OOS_FLOOR = 0.67` (`10/10` OOS abstention).
  * *Why Two-Clause Splitting Was Rejected:* Because single-query `Fusion.RRF` missed `Conjunct_Recall@5 >= 0.85` (`0.6000`), I prototyped deterministic two-predicate splitting with round-robin merging. On frozen validation, it raised `Conjunct_Recall@5` to `0.8000` (still `< 0.85`), **broke `A_B_Non_Inferiority`** (`VAL_021` regression in `warning_signs_severe`), **killed Wilcoxon `MRR@5` significance** ($p = 0.1138$), and **pushed CPU latency over budget** (`p50 = 31.09 ms`, `p95 = 61.86 ms`). I reverted it immediately.
* **Implementation:**
  * Added `RETRIEVAL_MODE` (`"dense"` default), `HYBRID_PREFETCH_LIMIT = 20`, and `HYBRID_DENSE_OOS_FLOOR = 0.67` in `config.py`.
  * Added fail-closed `get_sparse_bm25_embedding()` in [embeddings.py](guard-dengue/backend/app/retrieval/embeddings.py) (`RuntimeError` if `USE_FASTEMBED != "1"`—never falls back to incompatible MD5 hashing).
  * Wired dual `Prefetch` + `Fusion.RRF` (filtered strictly to `review_status == "approved"`), `with_vectors=["dense"]` OOS check, `_verified_collections` cache (avoiding repeated disk metadata stats), and `atexit.register(vector_store.close)` (`flock` teardown safety) in `vector_store.py`; added `_enrich_hybrid_clause()` and `section_path`-present SQLite parent skip (`engine.py:167`, saving ~2–3 ms/query to stay under the `30.0 ms` p50 gate) in `engine.py`.
  ```python
  # guard-dengue/backend/app/retrieval/vector_store.py
  results = self.client.query_points(
      collection_name=target_collection,
      prefetch=[
          models.Prefetch(query=dense_vector, using="dense", filter=query_filter, limit=active_prefetch),
          models.Prefetch(query=sparse_vector, using="sparse", filter=query_filter, limit=active_prefetch),
      ],
      query=models.FusionQuery(fusion=models.Fusion.RRF),
      limit=top_k, with_payload=True, with_vectors=["dense"],
  )
  hits = results.points
  if hits and effective_oos_floor > 0.0:
      qd_np = np.asarray(dense_vector, dtype=np.float32)
      max_dense_cos = max((float(np.dot(qd_np, np.asarray(h.vector["dense"], dtype=np.float32))) for h in hits if isinstance(getattr(h, "vector", None), dict) and h.vector.get("dense")), default=0.0)
      if max_dense_cos < effective_oos_floor:
          return []
  ```
  * Authored completely disjoint splits (`0` query/chunk overlap): [eval_dev_calib.jsonl](guard-dengue/backend/knowledge_pipeline/extracted/eval_dev_calib.jsonl) (`35` cases) and frozen [eval_dev_validation.jsonl](guard-dengue/backend/knowledge_pipeline/extracted/eval_dev_validation.jsonl) (`50` cases, `49` retrieval-eligible, `10` conjunctive).
* **Outcome (Frozen 50-Case Validation A/B):**

| Metric / Gate | Dense Baseline | Hybrid RRF Candidate | Requirement / Status |
| :--- | :---: | :---: | :--- |
| `Span_Recall@5` | `0.8878` | **`0.9592`** (`+7.14 pp`) | **PASS** (`>= 0.90`) |
| `Conjunct_Recall@5` | `0.5000` (`5/10`) | `0.6000` (`6/10`) | **FAIL** (`>= 0.85`) |
| `MRR@5` | `0.7585` | **`0.8289`** (`+0.0704`) | **PASS** (`Wilcoxon p = 0.0199`) |
| `A_B_McNemar_Significance` | — | `p = 0.1250` (`4 vs 0`) | **FAIL** (`< 0.05`; low discordance `b=4`) |
| `A_B_Non_Inferiority` | — | **PASS** (`0` regressions) | **PASS** |
| `Completeness` & `Medication Safety` | `1.0000` | **`1.0000`** | **PASS** |
| `Latency_p50_ms` (`p95`) | `15.92 ms` (`21.34 ms`) | **`28.90 ms`** (`40.49 ms`) | **PASS** (`< 30.0 ms`) |

  On the `eval_dev_smoke.jsonl` regression check (`N=29` eligible), Hybrid RRF also improved `Span_Recall@5` from `0.5345` to `0.7931` (`MRR@5`: `0.3891 -> 0.6523`, `Completeness = 1.00`, `Safety = 1.00`, `p50 = 28.47 ms`). Added `8` tests in [test_hybrid_retrieval.py](guard-dengue/backend/tests/test_hybrid_retrieval.py).

### Phase 8B: CI/CD Parity & Gate Consolidation

* **Why this decision:** `eval_runner.py` and `release_gates.py` duplicated the exact same 7 invariant gates and 2 retrieval thresholds, and `test_preflight_parity.py` had zero tests covering `expected_retrieval_mode="hybrid"`.
* **Benefits:** Eliminates policy drift between offline evaluation reports and CI release enforcement with a single source of truth, and ensures automated tests catch missing or empty sparse vectors before deployment.
* **Trade-offs:** Extracting a single shared `evaluate_scorecard_gates()` helper removes drift risk between evaluation and CI gating while preserving `RETRIEVAL_MODE = "dense"` as the safe default until Phase 8C or conjunctive improvements clear the remaining two gates.
* **Implementation:** Extracted `evaluate_scorecard_gates()` in `release_gates.py`, delegated `eval_runner.py` gate checks to it, and added `3` hybrid sparse-vector tests (`test_preflight_hybrid_success_live`, missing sparse schema failure, empty sparse indices failure) to [test_preflight_parity.py](guard-dengue/backend/tests/test_preflight_parity.py).
  ```python
  # guard-dengue/backend/knowledge_pipeline/release_gates.py
  def evaluate_scorecard_gates(
      *, provenance_failures: int, ing_recall: float, ing_precision: float,
      fail_closed: float, neg_invariants: float, completeness_acc: float,
      p50_latency: float, span_recall: float, conjunct_recall: float,
      include_retrieval_gates: bool = True, min_span_recall: float = 0.90,
      min_conjunct_recall: float = 0.85, max_p50_latency_ms: float = 30.0,
  ) -> List[Dict[str, Any]]:
  ```
* **Outcome:** `preflight.py --mode hybrid` passed (`425` chunks), `release_gates.py --baseline-mode` passed, and **`105/105` pytest tests passed in `6.58s`**.

---

## 5. Pending Future Work: Phase 8C (Dual-Clinician Locked Production Certification)

* **Why this is deferred:** A 50-case developer validation split where dense baseline already hits `0.8878` lacks statistical power for binary McNemar (`4 vs 0` gives $p = 0.1250$), and clinical deployment requires independent dual-clinician review on a much larger, cryptographically locked holdout.
* **Benefits:** Establishes clinical validity via independent two-clinician adjudication, delivers sufficient statistical power ($n_d \ge 6$ at $0$ losses, or $n_d \ge 25$ under $\chi^2$) to certify A/B superiority, and enforces tamper-proof SHA-256 holdout locking in CI.
* **Trade-offs:** Locking `100+` dual-clinician cases and decoupling benchmark lock metadata (`benchmark_lock_v1.json`) from runtime corpus manifests adds governance overhead, but prevents accidental holdout leakage and guarantees fail-closed certification.
* **How to Implement Phase 8C:**
  1. **Author `eval_release_locked.jsonl`:** `100+` clinical cases ($\ge 20$ per clinical slice, $\ge 15$ conjunctive, $\ge 15$ OOS/quarantined) reviewed by two clinicians, validated via `validate_benchmark.py` with zero overlap against smoke, calibration, and validation splits.
  2. **Pre-Evaluation Freeze & Conjunctive Decision:** Freeze model weights, thresholds, and code (optionally testing a single-pass post-fusion Slot-5 conjunctive re-ranker on `eval_dev_calib.jsonl` if switching default `RETRIEVAL_MODE` to `"hybrid"`).
  3. **Run & Cryptographically Lock:**
     ```powershell
     backend/.venv/Scripts/python.exe backend/knowledge_pipeline/eval_runner.py --benchmark backend/knowledge_pipeline/extracted/eval_release_locked.jsonl --release v0.1-dev --mode hybrid --enforce-retrieval-gate --output backend/knowledge_pipeline/extracted/locked_release_scorecard.json
     backend/.venv/Scripts/python.exe backend/knowledge_pipeline/release_gates.py --scorecard backend/knowledge_pipeline/extracted/locked_release_scorecard.json --manifest backend/knowledge_pipeline/extracted/release_manifest_v0.1-dev.json --benchmark backend/knowledge_pipeline/extracted/eval_release_locked.jsonl --enforce-locked
     ```
     Record `locked_benchmark_sha256` and `release_certified: true` in `release_manifest_v0.1-dev.json` (which `release_gates.py --enforce-locked` checks directly against `SHA256(eval_release_locked.jsonl)`, optionally synced into SQLite `release_manifests`) so CI fails closed on any benchmark tampering (`sys.exit(1)`).

---

## 6. Master Verification Ledger

| Check | Exact Command | Latest Verified Result |
| :--- | :--- | :--- |
| **Hybrid Preflight** | `backend/.venv/Scripts/python.exe backend/knowledge_pipeline/preflight.py --mode hybrid` | `PASSED` (`425` chunks in sync) |
| **Smoke Benchmark** | `backend/.venv/Scripts/python.exe backend/knowledge_pipeline/validate_benchmark.py --file backend/knowledge_pipeline/extracted/eval_dev_smoke.jsonl` | `PASSED` (`30` cases, `0` failures) |
| **Calibration & Validation Splits** | `backend/.venv/Scripts/python.exe backend/knowledge_pipeline/validate_benchmark.py --file backend/knowledge_pipeline/extracted/eval_dev_validation.jsonl` | `PASSED` (`35` calib + `50` val, `0` failures) |
| **Full Regression Suite** | `backend/.venv/Scripts/pytest.exe backend/tests/ -v` | **`105 passed in 6.58s`** |
| **Baseline Release Gate** | `backend/.venv/Scripts/python.exe backend/knowledge_pipeline/release_gates.py --scorecard backend/knowledge_pipeline/extracted/dense_baseline_scorecard.json --manifest backend/knowledge_pipeline/extracted/release_manifest_v0.1-dev.json --benchmark backend/knowledge_pipeline/extracted/eval_dev_smoke.jsonl --baseline-mode` | `PASSED` (`p50 = 19.18 ms`, all `7` invariants `PASS`) |
| **Hybrid A/B Gate (Frozen Val)** | `backend/.venv/Scripts/python.exe backend/knowledge_pipeline/release_gates.py --scorecard backend/knowledge_pipeline/extracted/hybrid_rrf_scorecard.json --baseline backend/knowledge_pipeline/extracted/dense_validation_scorecard.json --manifest backend/knowledge_pipeline/extracted/release_manifest_v0.1-dev.json --benchmark backend/knowledge_pipeline/extracted/eval_dev_validation.jsonl --enforce-ab-significance` | `Span_Recall@5 = 0.9592`, `Wilcoxon p = 0.0199`, `Non-Inferiority = PASS`, `p50 = 28.90 ms`; blocked on `Conjunct_Recall@5 = 0.6000` & `McNemar p = 0.1250` |
