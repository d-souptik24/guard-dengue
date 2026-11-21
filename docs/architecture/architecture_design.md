# GuardDengue: Architectural Design & Visual Specifications

> **Document Type:** Concept Architecture Specification (HLD, LLD, and System Data Flow)  
> **Target Audience:** Supervisory Review (Dr. Wazib) & Engineering Implementation  
> **Status:** Proposal & Concept Review (Fully Synchronized with Plan Version 2)  
> **Corpus / Source Reference:** [GuardDengue-Architecture-Review.md (Version 1)](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/plan/version_1/GuardDengue-Architecture-Review.md)  
> **Interactive Visual Artifacts (Showcase Quality Profile — 9/9 Validated):**
> - [High-Level Design (HLD) Diagram](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/architecture/guarddengue_hld.html)
> - [Low-Level Design (LLD) State Machine Diagram](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/architecture/guarddengue_lld_workflow.html)
> - [End-to-End System Data Flow Diagram](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/architecture/guarddengue_dataflow.html)

---

## 1. Executive Summary & Design Rationale

GuardDengue is an evidence-grounded, safety-aware educational framework designed to answer patient and caregiver inquiries about dengue fever. In clinical and consumer health settings, general-purpose Large Language Models (LLMs) pose severe risks of **hallucinations, diagnostic overreach, and contraindicated guidance** (such as suggesting NSAIDs like ibuprofen or aspirin, which exacerbate hemorrhagic dengue).

To address these vulnerabilities, GuardDengue enforces a strict architectural separation between **Offline Evidence Preparation** and **Online Educational Inference**, governed by deterministic clinical safety guardrails.

```
       ┌────────────────────────────────────────────────────────┐
       │                   Authoritative Docs                   │
       │                 (WHO, NVBDCP, MoHFW)                   │
       └───────────────────────────┬────────────────────────────┘
                                   │ (Docling AST & LlamaIndex Hierarchical Nodes)
                                   ▼
        OFFLINE TRACK   ┌─────────────────────┐
        ─────────────   │ Dual Knowledge Base │
                        │  (Neo4j + Qdrant)   │
                        └──────────┬──────────┘
                                   │ (Hybrid Dense + Sparse Retrieval)
                                   ▼
        ONLINE TRACK    ┌─────────────────────┐   Red-Flags / NSAID   ┌───────────────────────┐
        ────────────    │ Inbound User Prompt │──────────────────────►│ Zero-Latency Bypass   │
                        └──────────┬──────────┘  (Regex / Heuristic)  │ (Emergency Guideline) │
                                   │ Safe Query                       └───────────────────────┘
                                   ▼
                        ┌─────────────────────┐
                        │ LangGraph + SLM     │
                        │ (Constrained Draft) │
                        └──────────┬──────────┘
                                   │ (8-Check Claim Verification)
                                   ▼
                        ┌─────────────────────┐
                        │ Claim Verifier Gate │───► [Safe Release] or [Safe Abstention]
                        └─────────────────────┘
```

### Core Tenets Grounded in Literature (Plan Version 2)

1. **Separation of Medical Triaging from Generative RAG (Amugongo et al. 2025):**  
   Clinical red-flag dengue warning signs (persistent vomiting, severe abdominal pain, mucosal bleeding, lethargy, fluid accumulation) must **never** wait for an LLM/SLM generation loop. Furthermore, WHO guidelines stress that severe dengue frequently develops *after* fever subsides (the critical phase). Red flags are intercepted deterministically by the Screener Gateway with zero latency and routed to emergency escalation templates.
2. **Deterministic Contraindication Enforcement (WHO Guidelines):**  
   Aspirin, ibuprofen, diclofenac, and other NSAIDs are strictly contraindicated in suspected dengue due to platelet dysfunction and hemorrhage risks. GuardDengue implements hardcoded policy bypasses: medication queries trigger reviewed warnings explaining contraindication mechanisms and directing to paracetamol, rather than relying on generative model probabilistic adherence.
3. **Structured Table & Algorithmic Preservation (Docling + LlamaIndex):**  
   Clinical triage algorithms and fluid management charts cannot be flattened into raw Markdown without risking column-row corruption. We utilize **Docling** for layout-aware parsing alongside **structure-aware LlamaIndex nodes** (`HierarchicalNodeParser` and `MarkdownElementNodeParser` with `strip_headers=False`) to preserve parent-child section relationships and cell coordinates without synthetic summarization.
4. **Post-Generation Claim Verification (Basu & Huynh 2026 Taxonomy):**  
   Medical RAG failure modes are classified into three distinct categories:
   - *Input conflicts:* output ignoring user premise, symptoms, or stated patient constraints.
   - *Context conflicts:* internal inconsistencies or ungrounded assertions within the generated text.
   - *Fact conflicts:* contradictions against external authoritative medical consensus.  
   Every drafted response must pass an NLI Claim Verification Gate auditing these three failure types before publication.
5. **Guideline Retrieval over Unverified Reasoning (CoMT Context, Guo et al. 2025):**  
   While complex reasoning chains (such as Chain-of-Medical-Thought) assist multi-step diagnostics in research settings, they cannot substitute for deterministic retrieval of authoritative local clinical evidence. GuardDengue prioritizes explicit retrieval and citation over ungrounded internal parametric reasoning.

---

## 2. High-Level Design (HLD)

The High-Level Design defines the system boundaries, logical zones, component responsibilities, and inter-service communications.

**Interactive Diagram:** [`guarddengue_hld.html`](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/architecture/guarddengue_hld.html)  
*(Open in any modern browser for interactive zoom, dark/light themes, and animated trace motion).*

### Architectural Zones

| Zone | Primary Components | Responsibility |
| :--- | :--- | :--- |
| **Zone 1: Client & Ingress** | `client` (User App / Web UI)<br>`gateway` (Safety Screener Gateway) | Handles multi-device user interaction, TLS termination, session tokenization, and inbound prompt screening. |
| **Zone 2: Deterministic Safety** | `emergency` (Emergency Care Bypass)<br>`medsafety` (NSAID Safety Interceptor) | Evaluates deterministic heuristic rules; fires immediate emergency triage advice or NSAID avoidance warnings without invoking the LLM. |
| **Zone 3: Orchestration & Inference** | `orchestrator` (LangGraph Controller)<br>`generator` (Local SLM Engine: 8B/14B) | State machine execution, intent expansion, multi-source retrieval dispatch, prompt synthesis, and bounded revision. |
| **Zone 4: Dual Knowledge Base** | `docling` (Docling Ingestion Worker)<br>`qdrant` (Qdrant Hybrid Vector Store)<br>`neo4j` (Neo4j Clinical Knowledge Graph) | Offline multimodal parsing, 13-category metadata tagging, dense/BM25 indexing, and clinical entity/relationship storage. |
| **Zone 5: Verification & Delivery** | `verifier` (Claim Verification Gate)<br>`abstain` (Safe Abstention Handler)<br>`publisher` (Response Delivery Endpoint) | Sentence-level claim extraction, NLI entailment checking against retrieved evidence, safe fallback routing, and audit delivery. |

### Component Interaction Diagram

```
┌──────────────────┐
│ User Query / App │
└────────┬─────────┘
         │ 1. Inbound query
         ▼
┌─────────────────────────┐   Emergency Red-Flag    ┌───────────────────────────┐
│ Safety Screener Gateway ├────────────────────────►│ Emergency Guidance Bypass │
└────────┬────────────────┘   NSAID Contraposition  └─────────────┬─────────────┘
         │                                                        │
         │ 2. Safe Educational Request                            │
         ▼                                                        │
┌─────────────────────────┐    3. Hybrid Search    ┌───────────────────────────┐
│  LangGraph Controller   ├───────────────────────►│  Dual Knowledge Base      │
│                         │◄───────────────────────┤  (Qdrant + Neo4j)         │
└────────┬────────────────┘    4. Chunks & Triples └──────────────┬────────────┘
         │                                                        ▲
         │ 5. Grounded Prompt Context                             │ (Offline ETL)
         ▼                                                        │
┌─────────────────────────┐                               ┌───────┴─────────────┐
│    Local SLM Engine     │                               │ Docling Ingest Core │
└────────┬────────────────┘                               └─────────────────────┘
         │ 6. Draft Educational Response
         ▼
┌─────────────────────────┐   Contradiction / Hallucination   ┌───────────────────────────┐
│ Claim Verification Gate ├──────────────────────────────────►│  Safe Abstention Fallback │
└────────┬────────────────┘                                   └─────────────┬─────────────┘
         │ 7. Verified Grounded Claims                                      │
         ▼                                                                  ▼
┌───────────────────────────────────────────────────────────────────────────┴─┐
│                         Response Delivery Endpoint                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Low-Level Design (LLD) & State Machine Workflow

The Low-Level Design defines the internal lifecycle of an educational request through LangGraph, formalizing the state transitions, conditional edge gates, and terminal nodes.

**Interactive Diagram:** [`guarddengue_lld_workflow.html`](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/architecture/guarddengue_lld_workflow.html)  
*(Features swimlane partitioning across Client, Gateway, Safety, Retrieval, Synthesis, and Verification lanes).*

### Canonical LangGraph State Schema (Version 2 Specification)
```python
from typing import Literal, TypedDict

class State(TypedDict):
    question: str
    route: Literal["urgent", "education", "medication", "uncertain"]
    attempts: int
    evidence: list[dict]
    evidence_ok: bool
    draft: str
    verdict: Literal["pass", "revise", "reject"]
    answer: str
```

### Extended Production Payload Schema
```python
class DengueGraphState(State):
    query_sanitized: str
    session_id: str
    matched_rules: list[str]
    retrieved_chunks: list[dict]
    kg_triples: list[dict]
    extracted_claims: list[str]
    verification_score: float
    final_output: str
```

### State Machine Lifecycle Transitions

```
[user_in] ──► [screener]
                  │
                  ├── (route == "urgent") ────────────► [urgent_node]        (Terminal: Emergency Protocol)
                  ├── (route == "medication") ────────► [med_node]           (Terminal: Medication Warning)
                  ├── (route == "uncertain") ─────────► [uncertain_abstain]  (Terminal: Clarification / Fallback)
                  │
                  └── (route == "education") ─────────► [retrieve_node]
                                                              │
                                                              ▼
                                                        [evidence_gate]
                                                              │
                    ┌── (evidence_ok == False) ───────────────┴────── (evidence_ok == True) ──┐
                    ▼                                                                         ▼
             [abstain_node]                                                              [draft_node]
         (Terminal: Referral)                                                                 │
                                                                                               ▼
                                                                                        [verifier_node]
                                                                                               │
                    ┌── (verdict == "revise" & attempts < 2) ───► [revision_node] ────────────┤
                    │                                                                         │
                    ├── (verdict == "reject" or attempts >= 2) ─► [abstain_node]              │
                    │                                                                         │
                    └── (verdict == "pass") ──────────────────────────────────────────────────┴──► [publish_node]
                                                                                                   (Terminal: Verified Advice)
```

### Required Verification Behavior (The 8 Mandatory Checks)

Per Table 9 of the Architecture Review (Version 2), the Verification Gate must enforce:

| Check | Required Behavior |
| :--- | :--- |
| **1. Evidence Support** | Every medical factual claim must map to an eligible source passage or reviewed structured object. Verify support, not merely citation presence. |
| **2. Numeric & Structural Fidelity** | Compare numbers, units, inequality signs, populations, and table coordinates against canonical evidence. Do not rely on LLM similarity alone. |
| **3. Medication Policy** | Reject recommendations to use blocked medicines (NSAIDs: aspirin, ibuprofen, diclofenac) in suspected dengue. Permit avoidance explanations. |
| **4. Diagnosis & Triage Boundary** | Reject personalized diagnoses, unsupported severity scoring, and reassurance that symptoms are harmless. Citations do not authorize diagnostic claims. |
| **5. Contradictions & Uncertainty** | Do not silently pick between conflicting guidelines. Resolve through precedence, or acknowledge conflict and abstain from disputed advice. |
| **6. Input & Retrieval Integrity** | Treat user prompts and retrieved documents strictly as data, not instructions (prompt injection mitigation). |
| **7. Failure Handling** | Use explicit approved fallback messages and privacy-preserving error reporting. Never substitute missing evidence with model parametric memory. |
| **8. Output Release** | Do not stream unverified draft tokens. Publish only verified responses. Any generative rewrite requires re-verification. |

### Lane Allocation & Responsibilities
- **Client Lane:** `user_in` (captures payload) & `publish_node` (renders verified Markdown with clickable citations).
- **Gateway Lane:** `screener` (deterministic regex and keyword matchers for symptoms and drugs).
- **Safety Policy Lane (Exception Lane):** `urgent_node` (red-flag bypass), `med_node` (NSAID warning generator), & `uncertain_abstain` (safe fallback when query intent is ambiguous or unclassifiable).
- **Retrieval Lane:** `retrieve_node` (parallel dispatch to Qdrant vector index and Neo4j graph neighborhood) & `evidence_gate` (validates document recency, review status, and semantic score).
- **Synthesis Lane:** `draft_node` (prompt template restricting generation to retrieved context) & `revision_node` (targeted single-pass correction with error feedback).
- **Verification Lane:** `verifier_node` (NLI claim verification) & `abstain_node` (safe fallback when evidence is lacking or unverified).

---

## 4. End-to-End System Data Flow

The System Data Flow diagram depicts the dual data pathways across 5 functional stages: the **Offline Ingestion & Curation Track** and the **Online Retrieval & Synthesis Track**.

**Interactive Diagram:** [`guarddengue_dataflow.html`](file:///d:/USER%28dutta%29/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/architecture/guarddengue_dataflow.html)  
*(Built with `visual_preset: "signal-flow"` and `animation: "trace"` for stream visualization).*

### The 5 Functional Stages

```
┌──────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   STAGE 0    │   │     STAGE 1     │   │     STAGE 2     │   │     STAGE 3     │   │     STAGE 4     │
│   Sources    │──►│ Ingest & Triage │──►│ Knowledge Bases │──►│ Orchestrate/SLM │──►│ Verify & Output │
└──────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘   └─────────────────┘
```

#### Stage 0: Sources & Ingress
- **Authoritative Guidelines (`guidelines`):** Official PDF, DOCX, and HTML guidelines from the World Health Organization (WHO), National Vector Borne Disease Control Programme (NVBDCP, India), and CDC.
- **Inbound User Query (`patient_query`):** Multi-modal health inquiries from patients, families, or community health workers.

#### Stage 1: Ingestion & Triage
- **Docling Ingestion Engine (`docling_engine`):** Layout-aware document parsing. Retains coordinate grids, merged table headers, comparison operators, and branch decision logic.
- **Safety Screener (`safety_screener`):** Evaluates red-flag signs (hypotension, bleeding, acute vomiting) and contraindicated medications (aspirin, diclofenac, ibuprofen).

#### Stage 2: Knowledge Storage & Structuring
- **Neo4j Clinical Graph (`neo4j_graph`):** Graph database storing medical entities (`Symptom`, `Phase`, `WarningSign`, `Medication`, `PopulationGroup`) and directed relationships (`CONTRAINDICATED_IN`, `ESCALATES_TO`, `RESOLVES_IN`).
- **Qdrant Hybrid Store (`qdrant_vector`):** High-density vector database storing text chunks indexed with dense embeddings (e.g., BGE-small/MedEmbed) + BM25 sparse vectors, partitioned by the 13 clinical metadata categories.

#### Stage 3: Orchestration & Generation
- **LangGraph + Local SLM (`slm_engine`):** Aggregates retrieved text chunks and graph constraints into a prompt template that strictly limits generation to verified context. Uses a lightweight local SLM (e.g., Llama-3-8B / Qwen-2.5-7B) running locally or on-premises for patient privacy.

#### Stage 4: Verification & Delivery
- **Verifier Gate (`verification_gate`):** Natural Language Inference cross-encoder audits draft statements. Flagged contradictions or ungrounded assertions trigger a single revision pass or safe abstention.
- **Response Client (`response_delivery`):** Delivers verified educational output with citations, or clinician escalation instructions.

---

## 5. Controlled Clinical Evidence Contract & Metadata Taxonomy

All evidence stored in Qdrant and Neo4j must conform to the controlled 13-category metadata taxonomy and shared evidence schema (Plan Version 2, Section 1):

### Primary Evidence Fields

| Field | Required Meaning & Validation |
| :--- | :--- |
| `source` | Canonical source identifier or URL resolved through an approved source registry. Do not trust unverified publisher strings. |
| `publication_date` | Actual publication or revision date in ISO format (e.g., `2024-05-15`). Never substitute ingestion time. |
| `evidence_level` | Documented, reviewer-assigned classification (e.g., `Level-1-Guideline`, `Systematic-Review`, or explicitly `ungraded`). |
| `topic` | One or more controlled labels from the specified 13-category taxonomy (multi-label support). |

### Extended Provenance Payload
```json
{
  "source": "WHO-Dengue-Guidelines-2024",
  "document_id": "doc_who_dengue_2024_rev2",
  "document_version": "2.1",
  "content_hash": "sha256_8f9c2d...",
  "publication_date": "2024-05-15",
  "evidence_level": "Level-1-Guideline",
  "review_status": "clinician_approved",
  "reviewed_at": "2026-09-01T10:00:00Z",
  "topics": [
    "Warning signs",
    "Medication safety"
  ],
  "chunk_id": "chunk_sec4_p18_tbl2",
  "page": 18,
  "section_path": "Clinical Management > Warning Signs of Severe Dengue",
  "license": "CC-BY-NC-SA-4.0",
  "jurisdiction": "Global / WHO SEARO"
}
```

### Controlled 13-Topic Taxonomy
1. `Dengue basics`
2. `Transmission`
3. `Symptoms`
4. `Prevention`
5. `Hydration`
6. `Warning signs`
7. `Diagnosis`
8. `Myths`
9. `Children`
10. `Pregnancy`
11. `Medication safety`
12. `Outbreak awareness`
13. `Emergency guidance`

---

## 6. Recommended Technology Stack & Architecture Alternatives

### Final Recommended Technology Stack (Version 2 Specification)

| Layer | Recommended Technology | Technical Rationale & Scope |
| :--- | :--- | :--- |
| **Source Governance** | Approved Source Registry, SHA-256 Hashes | Establishes eligible evidence boundaries and makes every modification auditable. |
| **Document Parsing** | **Docling** | Local execution, layout-aware coordinate extraction, preserves table cell structure and branch logic. |
| **Table Storage** | Canonical structured table objects + HTML views | Preserves multi-column and numerical matrix relationships lost in flat text/Markdown. |
| **Diagram Interpretation** | VLM-assisted extraction (Qwen2.5-VL / Gemini) | Extracts decision tree logic; requires mandatory human clinician sign-off before ingestion. |
| **Chunking** | **Docling structure + LlamaIndex nodes** | Hierarchical parent-child nodes (`strip_headers=False`) preserve section path context. |
| **Retrieval Engine** | **Qdrant (Dense + Sparse BM25)** | High-throughput filtered hybrid search with strict payload metadata filtering. |
| **Knowledge Graph** | **Neo4j** | Curated clinical graph modeling explicit drug contraindications and disease phase transitions. |
| **Runtime Safety** | Versioned Python Rules & Approved Templates | Zero-latency emergency red-flag and NSAID contraindication handling. |
| **Orchestration** | **LangGraph** | Explicit state machine, conditional routing, bounded single-pass revision, and fallback abstention. |
| **Language Model** | Local SLM (8B / 14B: Llama 3.1 / Qwen 2.5) | Local privacy-preserving execution, strictly constrained to supplied context chunks. |
| **Claim Verification** | DeBERTa-v3 NLI Cross-Encoder | Audits generated text for input conflicts, context conflicts, and fact conflicts. |

### Explicitly Excluded Components (Per Version 2 Analysis)
- **RAPTOR Summaries:** Excluded as clinical evidence. Recursive abstractive summarization blurs critical numerical thresholds (e.g., platelet counts, hematocrit percentages) and creates synthetic hallucinations.
- **Unreviewed GraphRAG Safety Edges:** Excluded. Safety boundaries and drug contraindications must be hardcoded or clinician-reviewed, not probabilistically extracted by an LLM.
- **Autonomous Diagnosis / Personal Dosing:** Strictly prohibited by policy and verification gates.

---

## 7. Clinical Evaluation & Release Gates

Per Table 10 of Plan Version 2, GuardDengue must satisfy 9 comprehensive evaluation gates before release:

| Evaluation Area | What to Measure & Validate | Acceptance Criteria |
| :--- | :--- | :--- |
| **1. Extraction Fidelity** | Exact preservation of numbers, units, inequality operators, table coordinates, and flowchart branches. | 100% review on safety-critical guideline objects. |
| **2. Retrieval Recall** | Recall of required clinical evidence under active metadata filters, including low semantic similarity warnings. | $\ge 95\%$ recall on curated reference evidence sets. |
| **3. Grounding Accuracy** | Claim-level source attribution, citation accuracy, qualifier preservation, and safe handling of missing evidence. | 0 ungrounded medical assertions in verified outputs. |
| **4. Medication Safety** | Rejection of NSAIDs (aspirin, ibuprofen, diclofenac, naproxen), combination products, and adversarial bypasses. | **100% NSAID rejection rate** (zero tolerance). |
| **5. Emergency Handling** | Prompt identification of severe dengue red-flags, avoiding false reassurance across multi-turn interactions. | $\ge 95\%$ red-flag escalation sensitivity. |
| **6. Scope Control** | Strict rejection of requests for personal diagnoses, lab interpretation, personalized dosing, or severity scores. | 100% abstention on out-of-scope diagnostic requests. |
| **7. Reliability & Latency** | Sub-second tail latency on emergency bypass; graceful failure on index/model unavailability. | Zero unhandled exceptions; safe fallback guaranteed. |
| **8. Accessibility** | Readability and clarity in target languages without distortion of clinical meaning. | Clinician-verified plain language comprehension. |
| **9. Clinical Governance** | Named clinical owner, source update registry, audit logs, and instant rollback procedures. | Operational runbook signed off by clinical advisor. |

---

## 8. Meeting Talking Points for Dr. Wazib

When presenting these visual architectures to Dr. Wazib, highlight the following core design choices:
1. **Clinical Safety over Generative Freedom:** Why GuardDengue routes severe red-flags and contraindicated NSAID inquiries deterministically through zero-latency templates rather than trusting an LLM.
2. **Table & Matrix Integrity:** How Docling and LlamaIndex hierarchical nodes prevent the destruction of clinical triage tables that typically plagues standard RAG systems.
3. **Deterministic Graph Rules:** How Neo4j enforces contraindications (e.g., NSAID avoidance in thrombocytopenic phases) independently of semantic similarity search scores.
4. **Basu & Huynh Claim Verification:** How the 8-check Claim Verification Gate prevents hallucinations (input, context, and fact conflicts) from reaching the patient.
5. **Clear Phasing (Lean MVP vs. Full Research Stack):**
   - **Lean MVP:** Docling parser + Qdrant hybrid + SQLite rules + LangGraph + local Ollama (Llama-3-8B) for fast demonstrator.
   - **Full Research Stack:** Docling + Qdrant + Neo4j + LangGraph + vLLM + DeBERTa-v3 for publication-grade clinical rigor.

---
*Generated using Antigravity Archify Engine. Verified for showcase quality standards (9/9 checks passed).*
