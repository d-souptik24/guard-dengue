# GuardDengue: Frontend-Backend API Contract & Data Schemas

> **Document Type:** Technical Interface Specification (REST & SSE Streaming)  
> **Target Audience:** Backend Developers (FastAPI/LangGraph), Frontend Developers (React 19)  
> **Status:** REVISED API CONTRACT (PENDING FINAL REVIEW)  

---

## 1. Overview & Protocol Strategy

The GuardDengue backend serves the frontend via two primary protocols:
1. **Synchronous REST (`POST /api/chat`):** Used for single-turn complete responses, fallbacks, and automated test harnesses.
2. **Server-Sent Events (SSE) via POST (`POST /api/chat/stream`):** Used during live citizen conversations to stream incremental state transitions into the **Clinical Trace Inspector** while delivering verified educational answers to the citizen.

### 1.1 Strict Health Privacy Guarantee
To prevent citizen symptoms, medication questions, and session identifiers from leaking into plaintext browser histories, proxy access logs, and network caches, **GuardDengue strictly prohibits GET-based query-string streaming**. All requests are submitted via HTTP `POST` with encrypted JSON request bodies and consumed via `fetch()` with `ReadableStream`.

### 1.2 Verification Invariant (No Unverified Token Streaming)
In accordance with `GuardDengue-Architecture-Review.md` Section 5, the system **never streams unverified draft tokens**. The SSE connection streams workflow stage transitions (screening, retrieval, verification) to animate the staged loader and update the Clinical Trace Inspector, and releases the verified answer atomically in the `answer_publish` event once all safety checks have passed.

---

## 2. Canonical State & Route Contract

Matches the Plan Version 2 canonical LangGraph contract:

```typescript
export type RouteType = "urgent" | "medication" | "education" | "uncertain";

export type VerdictType = "pass" | "revise" | "reject" | "template_bypass";

export interface EvidenceMetadata {
  source: string;              // e.g., "WHO Clinical Management Guidelines 2024"
  publication_date: string;    // e.g., "2024-08-10" (ISO 8601)
  evidence_level:              // Controlled vocabulary:
    | "Level 1 (Global Clinical Practice Guideline)"
    | "Level 2 (National Public Health Protocol)"
    | "Level 3 (Public Health Technical Report)"
    | "Ungraded Clinical Review";
  topic: string[];             // Multi-label from the 13-category taxonomy
  chunk_id: string;            // e.g., "KB-WARN-001"
  corpus_release: string;      // e.g., "2026.09-v2-approved"
  document_version?: string;   // e.g., "v4.2"
  section_path?: string;       // e.g., "Section 3.2 > Critical Phase"
  score?: number;              // Qdrant cosine similarity (optional)
}

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}
```

---

## 3. REST Endpoint: `POST /api/chat`

### Request Payload:
```json
{
  "message": "আমার বাচ্চার জ্বর কমছে কিন্তু পেটে তীব্র ব্যথা হচ্ছে, কী করব?",
  "session_id": "sess_wb_8921a9c8",
  "language": "bn",
  "history": [
    {
      "role": "user",
      "content": "ডেঙ্গু জ্বর কত দিন থাকে?"
    },
    {
      "role": "assistant",
      "content": "সাধারণত ডেঙ্গুর তীব্র জ্বর ৩ থেকে ৭ দিন স্থায়ী হয়..."
    }
  ],
  "client_timestamp": "2026-11-20T08:00:00Z"
}
```

### Response Payload (`200 OK` — Urgent Emergency Route):
```json
{
  "session_id": "sess_wb_8921a9c8",
  "route": "urgent",
  "verdict": "template_bypass",
  "evidence_ok": true,
  "attempts": 0,
  "is_fallback": false,
  "answer": "এটি একটি গুরুতর সতর্কতামূলক লক্ষণ। ডেঙ্গুতে জ্বর কমার সময় (Days 3–7) প্লাজমা লিকেজের কারণে শক দেখা দিতে পারে। অবিলম্বে নিকটবর্তী হাসপাতালে যান বা ১০৮ / ১০২ নম্বরে অ্যাম্বুলেন্স ডাকুন।",
  "evidence": [
    {
      "source": "WHO Clinical Management Guidelines",
      "publication_date": "2024-08-10",
      "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
      "topic": ["Warning signs", "Emergency guidance"],
      "chunk_id": "KB-WARN-001",
      "corpus_release": "2026.09-v2-approved"
    }
  ],
  "safety_disclaimer": "এটি একটি স্বাস্থ্য সচেতনতামূলক বার্তা, চিকিৎসা প্রেসক্রিপশন বা রোগ নির্ণয় নয়। জরুরী অবস্থায় সরাসরি ডাক্তারের পরামর্শ নিন।",
  "telephony_action": {
    "recommended_call": "108",
    "helpline": "1800-313-444-222"
  },
  "metrics": {
    "total_latency_ms": 18,
    "zone2_screener_ms": 12,
    "model_generation_ms": 0,
    "nli_verification_ms": 0
  }
}
```

---

## 4. SSE Streaming Endpoint: `POST /api/chat/stream`

Initiated by the frontend using `fetch()` and `ReadableStream`:
- **Method:** `POST`
- **URL:** `/api/chat/stream`
- **Headers:** `Content-Type: application/json`, `Accept: text/event-stream`
- **Body:** Same JSON schema as `POST /api/chat`.

### Event Lifecycle Streamed Over Time:

#### Event 1: `event: screener_triage`
Emitted when `Zone 2 (Triage Screener)` resolves the query route:
```json
{
  "event": "screener_triage",
  "data": {
    "route": "education",
    "intent": "Diagnostic testing timeline",
    "matched_rules": ["lab_timing_ns1_igm"],
    "latency_ms": 25
  }
}
```

#### Event 2: `event: template_bypass` (Urgent & Medication Routes Only)
Emitted when a query matches deterministic emergency warning signs or medication safety policies, bypassing generative inference:
```json
{
  "event": "template_bypass",
  "data": {
    "route": "medication",
    "policy_rule": "nsaid_avoidance_suspected_dengue",
    "contraindicated_classes": ["NSAIDs", "Aspirin", "Ibuprofen"],
    "chronic_prescription_notice": "Do not stop prescribed medications without clinical consultation"
  }
}
```

#### Event 3: `event: retrieval_complete` (Educational Route Only)
Emitted when `Zone 4 (Hybrid Retrieval)` completes dense/sparse candidate retrieval:
```json
{
  "event": "retrieval_complete",
  "data": {
    "chunks_retrieved": 3,
    "evidence_ok": true,
    "top_source": "ICMR Guidelines 2024",
    "evidence_level": "Level 2 (National Clinical Laboratory Protocol)"
  }
}
```

#### Event 4: `event: revision_triggered` (Conditional — Max 1 Retry)
Emitted only if the draft contains a minor repairable grounding discrepancy:
```json
{
  "event": "revision_triggered",
  "data": {
    "attempt": 1,
    "reason": "Missing population qualifier for testing window"
  }
}
```

#### Event 5: `event: verification_audit` (Educational Route Only)
Emitted when `Zone 5 (Verification Gate)` audits drafted claims:
```json
{
  "event": "verification_audit",
  "data": {
    "verdict": "pass",
    "input_conflicts": 0,
    "context_conflicts": 0,
    "fact_conflicts": 0,
    "verified_claims_count": 3
  }
}
```

#### Event 6: `event: answer_publish`
Emitted with the final, certified educational response:
```json
{
  "event": "answer_publish",
  "data": {
    "answer": "ডেঙ্গু পরীক্ষার ধরণ নির্ভর করে লক্ষণ শুরুর সময়ের ওপর। প্রথম ১ থেকে ৫ দিনের মধ্যে (ভিরেমিয়া পর্ব) NS1 অ্যান্টিজেন পরীক্ষা বা RT-PCR করা উচিত।",
    "evidence": [
      {
        "source": "ICMR Guidelines for Laboratory Diagnosis",
        "publication_date": "2024-11-12",
        "evidence_level": "Level 2 (National Clinical Laboratory Protocol)",
        "topic": ["Diagnosis"],
        "chunk_id": "KB-DIAG-001",
        "corpus_release": "2026.09-v2-approved"
      }
    ],
    "citations_count": 1,
    "is_fallback": false
  }
}
```

#### Event 7: `event: answer_abstain` (Uncertain / Insufficient Evidence Route)
Emitted if evidence is missing, conflicting, or the question exceeds educational scope:
```json
{
  "event": "answer_abstain",
  "data": {
    "route": "uncertain",
    "verdict": "reject",
    "answer": "স্বাস্থ্য শিক্ষা ব্যবস্থা হিসেবে, পর্যাপ্ত অনুমোদিত ক্লিনিক্যাল প্রমাণের অভাবে আমি এই প্রশ্নের নিশ্চিত উত্তর দিতে পারছি না। অনুগ্রহ করে সরাসরি একজন রেজিস্টার্ড চিকিৎসকের পরামর্শ নিন।",
    "reason": "insufficient_verified_evidence",
    "referral_helpline": "1800-313-444-222"
  }
}
```

#### Event 8: `event: stream_error`
Emitted if an unrecoverable exception occurs:
```json
{
  "event": "stream_error",
  "data": {
    "code": "PIPELINE_ERROR",
    "message": "সাময়িক কারিগরি ত্রুটি। অনুগ্রহ করে জরুরী হেল্পলাইন ১৮০০-৩১৩-৪৪৪-২২২ নম্বরে যোগাযোগ করুন।",
    "is_fallback": true
  }
}
```

---

## 5. Multi-Turn Context Contract

To prevent unbounded token growth and protect citizen privacy:
1. **Client-Managed Bounded History:** The client transmits the last $N \le 4$ conversation turns in `history: Array<{role, content}>`.
2. **Ephemeral Server Session TTL:** If `session_id` is retained server-side for continuity, it is held strictly in volatile cache with a **15-minute inactivity Time-To-Live (TTL)** and zero persistent disk logging of raw symptom text.

---

## 6. Scale-Invariant Health Check Endpoint: `GET /api/health`

Supports both **Stage 1 (Colab T4 Prototype)** and **Stage 2 (University Server)** modes:

### Response Payload:
```json
{
  "status": "healthy",
  "version": "GuardDengue 2.0 (Plan v2)",
  "deployment_stage": "stage_1_prototype",
  "subsystems": {
    "fastapi_server": "ONLINE",
    "langgraph_workflow": "COMPILED",
    "vector_store": {
      "provider": "Qdrant",
      "mode": "embedded",
      "status": "READY"
    },
    "policy_engine": {
      "mode": "local_policy_artifact",
      "status": "LOADED",
      "rules_count": 48
    },
    "slm_engine": {
      "active_model": "Ministral-3B-Medical-v1",
      "quantization": "4-bit",
      "device": "cuda:0"
    }
  },
  "corpus_release": "2026.09-v2-approved"
}
```

---

## 7. Error Handling & Safe Fallback Matrix

| HTTP Status | Error Condition | System Action & Fallback Payload |
| :--- | :--- | :--- |
| **400 Bad Request** | Missing `message` or invalid JSON | Rejects gracefully with bilingual input validation tip. |
| **429 Too Many Requests**| Client flooding queries (> 30/min) | Rate-limits with civic retry message: *"অতিরিক্ত বার অনুরোধ করা হয়েছে। অনুগ্রহ করে ১ মিনিট পর চেষ্টা করুন।"* |
| **503 Service Degraded** | Inference timeout or dependency drop | **Deterministic Local Fallback:** Emits pre-compiled offline safety guidance with emergency helpline numbers (`108` / `102` & `1800-313-444-222`). Zero complete blackout. |
