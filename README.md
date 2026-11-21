<div align="center">

# GuardDengue

**Clinical safety guardrails for evidence-grounded dengue health awareness.**

[![Status: Academic Prototype](https://img.shields.io/badge/Status-Academic_Prototype-2563EB?style=flat-square)](https://github.com/d-souptik24/guard-dengue)
[![Stack](https://img.shields.io/badge/Stack-React_19_•_FastAPI_•_LangGraph-059669?style=flat-square)](https://github.com/d-souptik24/guard-dengue)
[![Retrieval](https://img.shields.io/badge/Retrieval-Qdrant_Hybrid-DC2626?style=flat-square)](https://qdrant.tech/)
[![License: MIT](https://img.shields.io/badge/License-MIT-64748B?style=flat-square)](LICENSE)

<br />

Academic project, A.K.C.S.I.T, University of Calcutta  
*Proposed for the Department of Health & Family Welfare, Government of West Bengal*

</div>

---

## Why GuardDengue Exists

During monsoon outbreaks across West Bengal, hospital triage desks face heavy queues. Patients and families routinely turn to search engines and conversational chatbots for quick guidance.

Standard language models are trained to produce fluent, reassuring answers. In acute dengue care, that helpful persona can be lethal:

| Scenario | Standard LLM Failure | Clinical Reality |
| :--- | :--- | :--- |
| **Fever drops on Day 4** | Tells the patient they are recovering. | Fever drop marks **defervescence** (Days 3–7), the critical window when capillary leak syndrome, hemorrhage, and shock occur. |
| **Headache & joint aches** | Suggests ibuprofen, aspirin, or combiflam. | NSAIDs impair platelet aggregation and cause gastrointestinal mucosal bleeding in thrombocytopenic patients. |
| **Child with high fever** | Tries to calculate weight-based paracetamol milligrams. | Dosage calculations for pediatric febrile illness require clinical oversight to prevent hepatic toxicity. |

GuardDengue maintains a strict separation: **it provides general health awareness, never personal medical diagnosis, treatment, or dose titration.** Emergency warning signs trigger immediate hospital escalation cards without touching a language model, while educational questions require guideline verification before publication.

---

## Architecture Flow

Inquiries pass through deterministic checks before any generative engine is queried:

```text
                        Inbound Citizen Query (English / বাংলা)
                                           │
                                           ▼
                           Deterministic Clinical Screener
                         (Zero-latency red-flag pattern rules)
                                           │
         ┌─────────────────┬───────────────┴───────────────┬─────────────────┐
         ▼                 ▼                               ▼                 ▼
    [ urgent ]       [ medication ]                  [ uncertain ]     [ education ]
         │                 │                               │                 │
   Emergency Card    Policy Intercept                Safe Refusal      Dual Qdrant
   Direct hospital   Explains bleeding risk;         Directs to        Retrieval
   call to 108/102   Paracetamol guidance only;      helpline and      (WHO/ICMR/NCVBDC)
   Zero LLM lag      Warns not to stop daily Rx      official portals        │
                                                                             ▼
                                                                       Bilingual SLM
                                                                       Draft Generation
                                                                             │
                                                                             ▼
                                                                     Post-Gen Verification
                                                                     (Claim conflict audit)
                                                                             │
                                                                      Passed │ Rejected
                                                                             ├──► Safe Refusal
                                                                             ▼
                                                                     Verified Response
                                                                     with Source Accordion
```

### Key Engineering Decisions

- **Zero-Latency Escalation:** Warning signs like persistent vomiting, severe abdominal pain, bleeding gums, or extreme lethargy bypass inference completely. The interface immediately renders hospital routing with one-tap dialing to **108 / 102 Ambulance Dispatch**.
- **Deterministic Medication Policy:** Painkiller inquiries route to hardcoded clinical guidance: paracetamol explanation, strict NSAID contraindications, and an explicit instruction never to discontinue chronic doctor-prescribed therapies without medical advice.
- **No Unverified Token Streaming:** LLMs can sound authoritative while hallucinating mid-sentence. GuardDengue holds output until drafted statements are audited against retrieved source guidelines.
- **Full Bilingual Parity:** Operates across English and Bengali (`বাংলা`) using native phrasing and regional typography (`Hind Siliguri`).

---

## Safety Rails Matrix

| Case | System Behavior | Clinical Rationale |
| :--- | :--- | :--- |
| **Defervescence Window** | Flags plasma leakage risks; highlights emergency signs if temperature falls suddenly. | Fever drop between Days 3–7 is when severe complications peak. |
| **Fever & Pain Relief** | Warns against aspirin, ibuprofen, naproxen, and diclofenac; references paracetamol. | NSAIDs damage gastric mucosa and inhibit platelet function. |
| **Chronic Prescriptions** | Reminds patients taking daily medications never to stop them on their own. | Unsupervised cessation of cardiovascular or endocrine drugs creates acute danger. |
| **Diagnostic Windows** | Explains NS1 Antigen testing (Days 1–5) versus IgM/IgG Antibody testing (post Day 5). | Requesting tests outside their diagnostic window yields misleading negative results. |
| **Pediatric Questions** | Shares general pediatric fever advice; refuses to compute exact home milligram doses. | Pediatric dosage calculation requires clinician confirmation. |
| **Home Remedies** | Notes that papaya leaf and herbal extracts lack RCT evidence and cannot replace hydration. | Unproven remedies delay oral rehydration salts (ORS) or hospital fluid therapy. |

---

## Technical Stack

| Layer | Tools | Role |
| :--- | :--- | :--- |
| **Interface** | React 19, Vite 8, TypeScript | Client application with English and Bengali script support |
| **Design & Tokens** | Tailwind CSS v4, Radix UI | Civic theme, verified WCAG AA contrast, high-contrast toggle |
| **Orchestration** | LangGraph, Python 3.10+ | State graph workflow, conditional routing, verification checkpoints |
| **API Layer** | FastAPI, Uvicorn | Asynchronous backend endpoints with SSE progress events |
| **Retrieval Engine** | Qdrant (Hybrid Dense + Sparse), Docling | Guideline chunk ingestion and hybrid keyword-semantic search |
| **Inference** | Small Language Models (SLMs) | Low-parameter local or server models for draft generation |

---

## Setup & Local Run

### Prerequisites
- Node.js 20+
- Python 3.10+
- Git

### 1. Repository Setup
```bash
git clone https://github.com/d-souptik24/guard-dengue.git
cd guard-dengue
```

### 2. Frontend Interface
```bash
cd frontend
npm install
npm run dev
```
The citizen interface opens at `http://localhost:5173`.

### 3. Backend Service
```bash
cd ../backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
The API server runs at `http://localhost:8000`.

---

## Clinical Evidence Grounding

The verification pipeline and safety logic are grounded in published health AI research:

- **RAG Vulnerabilities in Clinical Contexts:**  
  *Amugongo et al., PLOS Digital Health (2025)*  
  [https://doi.org/10.1371/journal.pdig.0000877](https://doi.org/10.1371/journal.pdig.0000877)  
  *Confirms that unstructured generative search without deterministic bypasses routinely fabricates medical claims.*

- **Hallucination Taxonomy in Healthcare AI:**  
  *Basu & Huynh, BMC Health Services Research (2026)*  
  [https://doi.org/10.1186/s12913-026-14851-1](https://doi.org/10.1186/s12913-026-14851-1)  
  *Supplies the 3-tier failure classification (Input, Context, and Fact conflicts) used during output auditing.*

### Indexed Knowledge Areas
The retrieval index covers official WHO, NVBDCP/NCVBDC, and ICMR guidance across 13 core categories:
1. Dengue viral biology and serotypes (DENV 1–4)
2. Vector transmission patterns (*Aedes aegypti* and *Aedes albopictus*)
3. Classical symptom presentation and fever differentiation
4. Larval control and household prevention
5. Oral fluid hydration and electrolyte replenishment
6. Warning signs during the defervescence transition
7. Phased diagnostic testing protocols (NS1 vs. IgM/IgG)
8. Evidence appraisal of folk remedies and misconceptions
9. Pediatric vigilance criteria
10. Pregnancy considerations and plasma volume changes
11. Analgesic safety and NSAID risks
12. Public health outbreak advisory routing
13. Inpatient hospitalization and referral indicators

---

## Emergency Contacts & Advisory

> **Civic Health Advisory:** GuardDengue is an academic prototype built for public awareness. It does not provide clinical diagnoses, individualized treatment plans, or drug prescriptions.
>
> If you or someone around you experiences red-flag symptoms (persistent vomiting, severe stomach pain, mucosal bleeding, difficulty breathing, or cold extremities):
> - **Emergency Ambulance Dispatch:** Call **`108`** or **`102`**
> - **West Bengal Health Helpline (Swasthya Bhawan):** Call **`1800-313-444-222`**

---

## Academic Context & Supervision

- **Academic Affiliation:** Academic project, A.K.C.S.I.T, University of Calcutta
- **Target Initiative:** Proposed for the Department of Health & Family Welfare, Government of West Bengal
- **Research Supervision:**
  - **Dr. Wazib** — Research Supervision (LLM/SLM & RAG Systems Architecture)
  - **Dr. Jhilam** — Research Supervision (Health Data Analytics & Clinical Evaluation)

### Project Contributors

- [Souptik Dutta](https://github.com/d-souptik24) (`@d-souptik24`)
- [Ayan Chakraborty](https://github.com/Ayan-chakraborty255) (`@Ayan-chakraborty255`)
- [Rupchand Naiya](https://github.com/usergithubrup) (`@usergithubrup`)
- [Swarnajit Paul](https://github.com/swarnajit006) (`@swarnajit006`)


---

<div align="center">
  <sub>Developed for evidence-grounded dengue health awareness in West Bengal. Grounded in verified clinical practice guidelines.</sub>
</div>
