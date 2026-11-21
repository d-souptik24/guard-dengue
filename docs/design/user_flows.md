# GuardDengue: Citizen & Clinical User Journeys (User Flows)

> **Document Type:** Step-by-Step Interactive User Journeys & State Transitions  
> **Target Audience:** Frontend Developers, QA Engineers, Clinical Evaluators, Examiners  
> **Status:** REVISED BASELINE SPECIFICATION (PENDING FINAL REVIEW)  

---

## 1. Flow Overview & Archetypes

GuardDengue serves two distinct user archetypes:
1. **The Citizen / Patient / Caregiver:**
   - Often experiencing elevated anxiety (e.g., family member with persistent high fever or dropping platelet count).
   - Needs immediate clarity, zero-latency emergency guidance, reassurance without medical overreach, and support in English or Bengali.
2. **The Clinical Supervisor / Academic Examiner (Dr. Wazib / Dr. Jhilam):**
   - Evaluates system architecture, LangGraph state transitions, Qdrant cosine similarities, Basu & Huynh hallucination checks, and inference telemetry.

---

## 2. User Flow 1: Acute Emergency Red-Flag Triage (Zone 2 Bypass)

### Scenario:
A mother in Kolkata writes: *"আমার বাচ্চার জ্বর কমছে কিন্তু পেটে খুব ব্যথা আর বারবার বমি হচ্ছে, এখন কী করব?"* (My child's fever is dropping, but has severe stomach pain and vomiting, what should I do?).

### Sequence Diagram & Interaction Steps:

```
[Citizen]                          [Zone 2 Screener]                 [Emergency Card]
   │                                       │                                 │
   │ 1. Submits query                      │                                 │
   ├──────────────────────────────────────►│                                 │
   │                                       │ 2. Scans for Warning Signs      │
   │                                       │    (severe stomach pain,        │
   │                                       │     vomiting, fever drops)      │
   │                                       │                                 │
   │                                       │ 3. Match: ROUTE = "urgent"      │
   │                                       ├────────────────────────────────►│
   │                                       │ (Zero-RAG Bypass: <20ms)        │ 4. Renders Red-Flag Card
   │                                       │                                 │    • Critical Defervescence Warning
   │                                       │                                 │    • Click-to-Dial 108 / 102
   │ 5. Reads urgent warning               │                                 │    • Nearest WB Health Facility
   │◄────────────────────────────────────────────────────────────────────────┤
   │                                       │                                 │
   │ 6. Clicks "Dial 108"                  │                                 │
   ├────────────────────────────────────────────────────────────────────────►│ Connects to Emergency Dispatch
```

### UX States & Behavioral Guarantees:
- **Zero Generative Latency:** The system does **not** wait for `Ministral-3B` or any LLM/SLM token generation.
- **Immediate Visual Priority:** A crimson emergency alert card overlays the screen with high-contrast text and a direct one-tap telephone dialer: `108` / `102` and `1800-313-444-222`.
- **Clinical Nuance:** Explains that the **critical phase** occurs during defervescence (Days 3–7) due to plasma leakage, urging hospital admission rather than home waiting.

---

## 3. User Flow 2: Medication Contraindication Intercept (NSAID Interceptor)

### Scenario:
A citizen asks: *"Can I take Combiflam or Ibuprofen for severe body ache and fever?"*

### Sequence Diagram & Interaction Steps:

```
[Citizen]                       [Zone 2 Med-Screener]           [Medication Advisory View]
   │                                     │                                  │
   │ 1. "Can I take Ibuprofen?"          │                                  │
   ├────────────────────────────────────►│                                  │
   │                                     │ 2. Matches NSAID Class Pattern:  │
   │                                     │    [ibuprofen, aspirin,          │
   │                                     │     combiflam, diclofenac]       │
   │                                     │                                  │
   │                                     │ 3. Route = "medication"          │
   │                                     ├─────────────────────────────────►│
   │                                     │                                  │ 4. Renders Amber Policy Card:
   │                                     │                                  │    • Strict OTC Contraindication Alert
   │                                     │                                  │    • Platelet/Hemorrhage Risk
   │                                     │                                  │    • Paracetamol Safe Guidance
   │                                     │                                  │    • Chronic Rx Warning (DO NOT STOP
   │                                     │                                  │      prescribed medicines without doctor)
   │ 5. Reads Clear Guidance             │                                  │
   │◄───────────────────────────────────────────────────────────────────────┤
```

### Safety Policy Enforced:
- The system explains *why* OTC NSAIDs must be avoided (antiplatelet effects + gastric mucosal erosion leading to severe hemorrhage in thrombocytopenic patients).
- **Prescription Medication Protection:** Explicitly instructs patients taking long-term prescribed medicines (e.g., cardiological aspirin) **never to discontinue their prescribed therapy unilaterally**, directing them to call their physician or Swasthya Bhawan Helpline `1800-313-444-222`.

---

## 4. User Flow 3: Evidence-Grounded Educational Inquiry (Bilingual RAG)

### Scenario:
A user asks: *"ডেঙ্গু হলে কোন কোন পরীক্ষা করা উচিত এবং কখন?"* (Which tests should be done for dengue and when?).

```
[Citizen]           [Zone 2]        [Zone 4: Qdrant]    [Zone 3: Ministral]    [Zone 5: Verifier]    [Sahayata Desk UI]
   │                   │                    │                   │                     │                    │
   │ 1. Submits query via POST /api/chat/stream │               │                     │                    │
   ├──────────────────►│                    │                   │                     │                    │
   │                   │ 2. Route="education"│                  │                     │                    │
   │                   ├───────────────────►│                   │                     │                    │
   │                   │                    │ 3. Hybrid Search  │                     │                    │
   │                   │                    │    (bge-m3 dense +│                     │                    │
   │                   │                    │     sparse BM25)  │                     │                    │
   │                   │                    ├──────────────────►│                     │                    │
   │                   │                    │    Top evidence   │ 4. Drafts response  │                    │
   │                   │                    │                   │    in fluent Bengali│                    │
   │                   │                    │                   ├────────────────────►│                    │
   │                   │                    │                   │                     │ 5. Verification:   │
   │                   │                    │                   │                     │    • Input Check   │
   │                   │                    │                   │                     │    • Context Check │
   │                   │                    │                   │                     │    • Fact Check    │
   │                   │                    │                   │                     │    Verdict: PASS   │
   │                   │                    │                   │                     ├───────────────────►│
   │                   │                    │                   │                     │                    │ 6. Staged Loader resolves
   │                   │                    │                   │                     │                    │    Publishes Verified Answer
   │ 7. Citizen reads verified guidance + expands WHO/ICMR citation accordion                              │    + Evidence Accordion
   │◄──────────────────────────────────────────────────────────────────────────────────────────────────────┤
```

### Verification & Attestation:
- **No Token Streaming:** The UI displays a staged verification loader (*"Checking guidelines..."* $\rightarrow$ *"Verifying clinical safety rules..."*) while the LangGraph node executes, releasing the complete verified answer on `answer_publish`.
- **Clinical Nuance Delivered:** Explains that **NS1 Antigen ELISA / RT-PCR** is indicated in Days 1–5 (viremic phase), whereas **IgM/IgG Antibody testing** is reliable only after Day 5.
- Displays metadata chip: `ICMR Guidelines for Laboratory Diagnosis 2024 (Level 2 National Protocol)`.

---

## 5. User Flow 4: Out-of-Scope / Vague Query (Safe Abstention)

### Scenario:
A user asks an ungrounded or ambiguous question: *"Can dengue be cured with homeopathic drops?"* or *"My platelet count is 85,000, calculate my discharge date."*

1. **System Step 1:** Zone 2 / Zone 3 detects absence of eligible clinical evidence in the authorized corpus (`evidence_ok == False`).
2. **System Step 2:** State transitions to `uncertain_abstain` node.
3. **Citizen View:**
   - A calm, neutral **Safe Abstention Card** is rendered.
   - Text: *"স্বাস্থ্য শিক্ষা ব্যবস্থা হিসেবে, পর্যাপ্ত অনুমোদিত ক্লিনিক্যাল প্রমাণের অভাবে আমি এই প্রশ্নের নিশ্চিত উত্তর দিতে পারছি না। অনুগ্রহ করে সরাসরি একজন রেজিস্টার্ড চিকিৎসকের পরামর্শ নিন বা স্বাস্থ্য হেল্পলাইন ১৮০০-৩১৩-৪৪৪-২২২ নম্বরে যোগাযোগ করুন।"* (As a health education system, due to lack of approved clinical evidence, I cannot provide a definitive answer. Please consult a registered medical practitioner or call the health helpline 1800-313-444-222).
   - Zero hallucination or invented answers.

---

## 6. User Flow 5: Academic Supervisor & Examiner Review (Dr. Wazib Mode)

### Scenario:
Dr. Wazib or an external B.Tech IT viva examiner clicks the **"Inspector Mode"** button on the top masthead during a project demonstration.

### Interaction Steps:
1. **Drawer Slide-Over:** The **Clinical Trace Inspector** smoothly animates from the right edge ($420\text{px}$ width).
2. **Real-Time Pipeline Trace:**
   - **Zone 2 Screener Badge:** Shows active classification (`ROUTE: EDUCATION`).
   - **Deployment Stage Telemetry:** Displays deployment mode (Stage 1 Prototype Colab T4: Embedded Qdrant, Local Policy Artifact, `Ministral-3B-Medical-v1` active).
   - **Retrieval Engine View:** Displays top matching chunk ID (`KB-DIAG-001`), source (`ICMR 2024`), and cosine score (`0.8842`).
   - **Basu & Huynh Taxonomy Audit:**
     - `Input-conflicting: 0`
     - `Context-conflicting: 0`
     - `Fact-conflicting: 0`
     - `Verdict: PASS`
3. **Inspector Close:** Clicking "Close Inspector View" or pressing `Esc` collapses the panel smoothly, leaving the citizen chat completely undisturbed.
