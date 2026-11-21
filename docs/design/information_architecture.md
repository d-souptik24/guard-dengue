# GuardDengue: Information Architecture (IA) & Sitemap

> **Document Type:** Structural Information Architecture & Navigation Hierarchy  
> **Target Audience:** Frontend Engineers, UX Designers, Clinical Reviewers  
> **Status:** REVISED ARCHITECTURE BASELINE (PENDING FINAL REVIEW)  
> **Compliance:** UX4G 2.0 & Guidelines for Indian Government Websites (GIGW 3.0)  

---

## 1. System Navigation Hierarchy (Sitemap)

The GuardDengue portal is organized into a clean, shallow hierarchy designed to minimize citizen friction during health queries while providing researchers with full trace visibility:

```
GuardDengue Portal (Root: /)
├── 1.0 Top Accessibility Bar (GIGW Strip)
│   ├── 1.1 Skip to Main Content
│   ├── 1.2 Font Size Scaler (A-, A, A+)
│   ├── 1.3 High-Contrast Toggle ([data-contrast="high"])
│   └── 1.4 Language Selector (English / বাংলা)
│
├── 2.0 Official WB Health Masthead & Emergency Hub
│   ├── 2.1 Academic Affiliation & GuardDengue Teal Heart-and-Cross Shield
│   ├── 2.2 Department of Health & Family Welfare Bilingual Title
│   ├── 2.3 Telephony Quick-Dial (Ambulance: 108 / 102)
│   ├── 2.4 State Health Helpline (1800-313-444-222)
│   └── 2.5 Clinical Inspector Toggle (Supervisor Mode for Dr. Wazib)
│
├── 3.0 Integrated Emergency Ribbon (Dynamic Zone 2 Warning)
│   ├── 3.1 Critical Defervescence Warning (Days 3–7)
│   └── 3.2 Immediate Hospital Referral Action (Click-to-Call 108)
│
├── 4.0 Citizen Action Bento Grid (Above-the-Fold Quick Navigation)
│   ├── 4.1 "জ্বর কমার সময় বিপদ" (Critical Warning Signs)
│   ├── 4.2 "কী ওষুধ খাওয়া নিষেধ?" (Medication Precautions & NSAID Avoidance)
│   ├── 4.3 "জল ও ইলেক্ট্রোলাইট" (Oral Hydration & Fluid Therapy)
│   ├── 4.4 "ডেঙ্গু টেস্টের সঠিক সময়" (Laboratory Testing Protocol: NS1 vs IgM/IgG)
│   └── 4.5 "নিকটবর্তী স্বাস্থ্য কেন্দ্র" (West Bengal Swasthya Kendra Directory)
│
├── 5.0 Swasthya Dengue Sahayata Desk (Conversational Interface)
│   ├── 5.1 Query Input Dock (Bilingual text input, Quick prompts)
│   ├── 5.2 Staged Verification Loader ("Checking guidelines..." → "Verifying safety...")
│   ├── 5.3 Conversation Stream (4 Outcome States)
│   │   ├── 5.3.1 Citizen Message Turn
│   │   ├── 5.3.2 Urgent Escalation Card (108 Ambulance Call Action)
│   │   ├── 5.3.3 Medication Safety Card (NSAID Avoidance + Prescribed Meds Caution)
│   │   ├── 5.3.4 Verified Educational Response Card + Evidence Accordion
│   │   └── 5.3.5 Safe Abstention Card (Insufficient Evidence / Referral)
│   └── 5.4 Evidence Accordion Fields
│       ├── Source Authority (WHO, NCVBDC, ICMR)
│       ├── Evidence Level (Level 1 / Level 2)
│       ├── Publication / Update Date
│       └── Multi-Label Topic Category
│
├── 6.0 Clinical Trace Inspector (Supervisor Side Drawer)
│   ├── 6.1 Zone 2 Screener Route Verdict
│   ├── 6.2 LangGraph 4-Stage Lifecycle Animation
│   ├── 6.3 Qdrant Dense/Sparse Hybrid Retrieval Results
│   ├── 6.4 Neo4j / Local Policy Fired Avoidance Rules
│   ├── 6.5 Basu & Huynh Verification Scorecard
│   └── 6.6 Telemetry & Deployment Stage Metrics (Stage 1 Colab T4 vs Stage 2 Server)
│
└── 7.0 Official Government-Style Footer (wb.gov.in Pattern)
    ├── 7.1 Centered Pipe-Separated Links (Home | About | Contact | Disclaimers)
    ├── 7.2 Statutory Medical Disclaimer (Education only, never diagnosis/prescribing)
    └── 7.3 Academic B.Tech IT Research Credits
```

---

## 2. Content Hierarchy: 13 Clinical Categories Mapping

The 13 knowledge base categories specified by the university and health department are mapped into citizen-friendly taxonomy groups:

| Knowledge Category | Citizen Intent Label (EN) | Citizen Intent Label (বাংলা) | Architectural Priority |
| :--- | :--- | :--- | :--- |
| **Emergency guidance** | Immediate Emergency Signs | অবিলম্বে হাসপাতালে যাওয়ার লক্ষণ | **Critical (Zone 2 Bypass)** |
| **Warning signs** | Warning Signs in Defervescence | জ্বর কমার সময় সতর্কতামূলক লক্ষণ | **Critical (Zone 2 Bypass)** |
| **Medication safety** | Safe Fever Medications & NSAID Risk | ব্যথার ও জ্বরের নিরাপদ ওষুধ | **High (Zone 2 Intercept)** |
| **Hydration** | Fluid & Electrolyte Care | তরল ও ওআরএস (ORS) গ্রহণ | **High (RAG Tier 1)** |
| **Children** | Pediatric Warning Signs & Care | শিশুদের ডেঙ্গু লক্ষণ ও সতর্কতা | **High (RAG Tier 1)** |
| **Pregnancy** | Dengue Precautions in Pregnancy | গর্ভাবস্থায় ডেঙ্গু ও করণীয় | **High (RAG Tier 1)** |
| **Diagnosis** | Blood Tests & Timing (NS1 vs IgM) | রক্তের পরীক্ষা ও সঠিক সময় | **Medium (RAG Tier 2)** |
| **Symptoms** | Common Dengue Symptoms | ডেঙ্গুর প্রাথমিক লক্ষণ | **Medium (RAG Tier 2)** |
| **Dengue basics** | What is Dengue? (Serotypes & ADE) | ডেঙ্গু কী ও কীভাবে হয়? | **Medium (RAG Tier 2)** |
| **Transmission** | Mosquito Vectors & Prevention | কীভাবে ডেঙ্গু ছড়ায়? | **Medium (RAG Tier 2)** |
| **Prevention** | Household Mosquito Control | মশা নিধন ও গৃহস্থালি প্রতিরোধ | **Standard (RAG Tier 3)** |
| **Myths** | Papaya Leaf & Antibiotic Facts | পেঁপে পাতা ও অ্যান্টিবায়োটিক বিভ্রান্তি | **Standard (RAG Tier 3)** |
| **Outbreak awareness** | West Bengal Ward & District Alerts | স্থানীয় প্রাদুর্ভাব সতর্কতা | **Standard (Redirect to Portal)** |

---

## 3. Data Flow & Routing Matrix

```
                      CITIZEN QUERY INPUT
                               │
                               ▼
               ┌───────────────────────────────┐
               │    Zone 2: Triage Screener    │
               │ (medfit-llm-3B Classifier)    │
               └───────────────┬───────────────┘
                               │
       ┌───────────────────────┼────────────────────────┬──────────────────────┐
       ▼                       ▼                        ▼                      ▼
 [URGENT EMERGENCY]     [MEDICATION SAFETY]     [EDUCATIONAL INQUIRY]    [UNCERTAIN / VAGUE]
       │                       │                        │                      │
       ▼                       ▼                        ▼                      ▼
 ┌───────────┐           ┌───────────┐            ┌───────────┐          ┌───────────┐
 │ Emergency │           │ NSAID     │            │ Hybrid    │          │ Safe      │
 │ Guidance  │           │ Avoidance │            │ Retrieval │          │ Abstain   │
 │ Card      │           │ Advisory  │            │ (Qdrant)  │          │ Card      │
 └─────┬─────┘           └─────┬─────┘            └─────┬─────┘          └─────┬─────┘
       │                       │                        │                      │
       ▼                       ▼                        ▼                      ▼
 108 / 102 Dial          Paracetamol Only         LangGraph Draft        Referral to
 Hospital Direct         Do Not Stop Rx           & NLI Verify           1800-313-444-222
```

---

## 4. Navigation Rules & Screen Real-Estate Allocations

1. **Desktop Viewport ($\ge 1024\text{px}$):**
   - **Header Area ($122\text{px}$ total height):** Accessibility strip ($34\text{px}$) + WB Health Saffron Masthead ($88\text{px}$).
   - **Main Content (Above-the-Fold):** Symmetrically centered container (`max-w-7xl mx-auto px-6 pt-4`).
     - Left Column ($35\%$ width): Citizen Action Bento Grid & Quick Telephony Directory.
     - Right Column ($65\%$ width): Swasthya Dengue Sahayata Desk (Conversation stream + $52\text{px}$ sticky input).
   - **Inspector Panel:** Slides out from the right as a $420\text{px}$ drawer, without obstructing citizen view.
2. **Mobile Viewport ($< 768\text{px}$):**
   - **Header:** Sticky compact masthead with hamburger menu for accessibility controls and direct `108` phone button.
   - **Bento Grid:** Compact swipeable quick-action cards directly above the conversation stream.
   - **Chat Input:** Anchored sticky bar at the bottom with safe-area padding (`pb-safe`) for mobile viewports.

---

## 5. Metadata Schema Integration

Every educational response rendered in the interface must bind to the following metadata contract:

```typescript
interface EvidenceContract {
  source: string;              // e.g., "WHO Clinical Management Guidelines 2024"
  publication_date: string;    // e.g., "2024-08-10" (ISO 8601)
  evidence_level:              // Controlled vocabulary:
    | "Level 1 (Global Clinical Practice Guideline)"
    | "Level 2 (National Public Health Protocol)"
    | "Level 3 (Public Health Technical Report)"
    | "Ungraded Clinical Review";
  topic: string[];             // Multi-label from the 13-category taxonomy
  chunk_id: string;            // Canonical chunk identifier (e.g., "KB-WARN-001")
  corpus_release: string;      // e.g., "2026.09-v2-approved"
  score?: number;              // Qdrant cosine similarity (optional)
}
```

This guarantees full provenance and regulatory auditability.
