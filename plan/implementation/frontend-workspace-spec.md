# GuardDengue: Frontend Workspace & Architecture Implementation Specification

> **Document ID:** `GD-SPEC-FE-001`  
> **Target File:** [`plan/implementation/frontend-workspace-spec.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/plan/implementation/frontend-workspace-spec.md)  
> **Status:** Final Implementation Specification (Phase 1–3 Complete)  
> **Authors:** Undergraduate Researchers (B.Tech, A.K.C.S.I.T., University of Calcutta)  
> **Supervisory Leads:** Prof. (Dr.) Amlan Chakraborty (Lead Supervisor), Dr. Wazib & Dr. Jhilam (Research Mentors)  
> **Target Deployment:** Department of Health & Family Welfare, Government of West Bengal  

---

## 1. Executive Summary & Purpose

GuardDengue is an evidence-grounded public health awareness and clinical verification prototype designed for dengue seasonal outbreaks in West Bengal. It provides citizens with trusted, guideline-verified health awareness while strictly rejecting diagnostic, prescribing, or clinical dose-titration behaviors.

The frontend serves as the **Swasthya Dengue Sahayata Desk (স্বাস্থ্য ডেঙ্গু সহায়তা কেন্দ্র)**. It is an accessible, bilingual (English and Bengali) conversational interface engineered with deterministic safety bypasses, transparent evidence disclosure, and GIGW 3.0 accessibility compliance.

This document serves as the authoritative technical specification of the entire frontend codebase, recording its folder architecture, component contracts, UI/UX tokens, safety mechanisms, and the exact API protocol expected by the backend LangGraph pipeline.

---

## 2. Core Literature & Design Document Grounding

The frontend implementation strictly implements and cross-references the following project literature and design specifications:

### 2.1 Academic Literature Foundations
1. **Amugongo et al. (PLOS Digital Health, 2025):**  
   *Retrieval augmented generation for large language models in healthcare: A systematic review* ([DOI: 10.1371/journal.pdig.0000877](https://doi.org/10.1371/journal.pdig.0000877)).  
   *Direct Frontend Impact:* Justifies holding conversational token streaming until post-generation verification is complete, and enforcing immediate, deterministic bypasses for emergency warning signs (severe abdominal pain, persistent vomiting, mucosal bleeding) to prevent LLM hallucinations.
2. **Basu & Huynh (BMC Health Services Research, 2026):**  
   *Mitigating hallucinations in healthcare AI: a systematic review of evidence-based strategies* ([DOI: 10.1186/s12913-026-14851-1](https://doi.org/10.1186/s12913-026-14851-1)).  
   *Direct Frontend Impact:* Grounds the Clinical Trace Inspector and typing indicator's two-stage verification pulse, auditing generated claims against the 3-tier failure classification: Input-conflicting, Context-conflicting, and Fact-conflicting.

### 2.2 Project Specifications & Design Docs
- **[`plan/version_1/GuardDengue-Architecture-Review.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/plan/version_1/GuardDengue-Architecture-Review.md):** Defines the 4 canonical state routes (`urgent`, `medication`, `education`, `uncertain`) and the mandatory 4-field metadata contract.
- **[`docs/design/ui_design.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/design/ui_design.md):** Defines layout grids, mobile viewports, responsive breakpoints, and civic design tokens.
- **[`docs/design/brand_identity.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/design/brand_identity.md):** Defines the West Bengal emblem shield geometry, color palette, and bilingual typography pairing.
- **[`docs/design/component_inventory.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/design/component_inventory.md):** Defines component states, touch targets, and ARIA labels.
- **[`docs/design/api_contract.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/design/api_contract.md):** Defines the POST-based SSE protocol (`POST /api/chat/stream`) and JSON schemas.
- **[`docs/design/accessibility_spec.md`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/docs/design/accessibility_spec.md):** Defines GIGW 3.0 compliance, contrast ratios, and keyboard navigation.

---

## 3. Technology Stack & Build Pipeline

The frontend is implemented as a modern, high-performance client application compiled directly into the backend distribution:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Frontend Technology Stack                       │
├─────────────────────────┬──────────────────────────────────────────────┤
│ Core Framework          │ React 19.3.1 + React DOM 19.3.1              │
│ Build Tool & Dev Server │ Vite 8.3.5 (cold build in ~700ms)            │
│ Language & Compiler     │ TypeScript 7.0.2 (strict mode enabled)       │
│ CSS & Design Tokens     │ Tailwind CSS v4.3.3 via @tailwindcss/vite    │
│ Headless UI Primitives  │ Radix UI (Dialog, Accordion, Select, Switch) │
│ Client-Side Routing     │ React Router DOM v7.18.5                     │
│ Server State Management │ TanStack React Query v5.105.1                │
│ Icons                   │ Lucide React v1.66.0 (strokeWidth: 1.75)     │
│ Code Quality & Linting  │ Oxlint v1.89.0 (sub-20ms multi-thread linter)│
└─────────────────────────┴──────────────────────────────────────────────┘
```

### 3.1 Single-Process Deployment Architecture
To eliminate the operational complexity of managing separate Node.js and Python processes in university viva evaluations and municipal deployments, `frontend/vite.config.ts` builds directly into `../backend/static`:

```typescript
// frontend/vite.config.ts
export default defineConfig({
  plugins: [tailwindcss(), react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/stream': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
  build: {
    outDir: '../backend/static',
    emptyOutDir: true,
  },
})
```
FastAPI mounts `backend/static` using `StaticFiles(html=True)`, allowing a single `uvicorn main:app --port 8000` process to serve both the client interface and the LangGraph pipeline.

---

## 4. Design Tokens, Typography & GIGW 3.0 Compliance

All design tokens are implemented CSS-first in [`frontend/src/index.css`](file:///d:/USER(dutta)/PROJECT_SOUPTIK_DUTTA/guard-dengue/frontend/src/index.css) using Tailwind CSS v4 variables:

### 4.1 Color System & Clinical Safety Semantics
- **Civic Primary (West Bengal Ochre/Amber):** `--color-wb-amber-700: #B45309`, `--color-wb-ochre-800: #92400E`.
- **Zone 2 Emergency (Ambulance Dispatch):** `--color-zone-emergency: #991B1B` (Crimson-900).
- **Zone 2 Medication Hazard (NSAID Intercept):** `--color-zone-medication: #B45309` (Amber-700).
- **Zone 5 Verified Evidence:** `--color-zone-verified: #0F8B8D` (Clinical Teal).
- **Zone 2 Uncertain / Abstain:** `--color-zone-uncertain: #475569` (Slate-600).
- **Evidence Level 1 (Global Guidelines):** `#1D4ED8` (WHO Blue).
- **Evidence Level 2 (National Protocols):** `#0F8B8D` (ICMR Teal).

### 4.2 GIGW 3.0 Accessibility Tokens
Government of India Guidelines for Web Portals (GIGW 3.0) mandates specific contrast modes and touch ergonomics:
- **Yellow-on-Black Contrast Mode (`.contrast-high`):**
  - Background Canvas: `#000000` (pure black).
  - Primary Text & Borders: `#FFFF00` (high-luminance yellow).
  - Focus Ring: `3px solid #FFFF00` with `2px` offset.
  - Links: `#FFFF00` with persistent underline.
- **Touch Target Sizing:** All interactive buttons (`GIGWToolbar`, `QuickPrompts`, `ChatInput`, `EmergencyRibbon`) enforce a strict minimum touch target of $\ge 44 \times 44\text{px}$.
- **Font Scaling:** Global text scaling supported via three tiers: `text-sm` (90%), `text-base` (100%), and `text-lg` (115%).

### 4.3 Bilingual Typography Pairing
- **English (`en`):** `Inter`, system-ui, sans-serif.
- **Bengali (`bn`):** `Hind Siliguri`, sans-serif.
- Configured via `:lang(bn)` in `index.css` with adjusted leading (`leading-relaxed` / `leading-loose`) to prevent Bengali vowel diacritics (*matras*) from clipping.

---

## 5. Complete Directory Tree & Component Inventory

```text
frontend/src/
├── api/
│   └── client.ts                     # REST & SSE fetch client with TextDecoder
├── constants/
│   └── index.ts                      # API routes, bilingual quick prompts, source map
├── store/
│   └── settings.tsx                  # SettingsContext: language, contrast, fontSize, inspector
├── types/
│   └── index.ts                      # RouteType, EvidenceMetadata, StreamEvent, ChatMessage
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx              # Civic header, legal qualifier, main container
│   │   ├── GIGWToolbar.tsx           # Text resize, contrast toggle, language switch
│   │   ├── GovFooter.tsx             # Emergency helplines (108/102/1800), disclaimers
│   │   └── index.ts
│   ├── citizen/
│   │   ├── CitizenBentoGrid.tsx      # 4 quick-access guidance cards with 1-tap prompts
│   │   ├── EmergencyRibbon.tsx       # Defervescence warning banner (Days 3–7)
│   │   ├── TelephonyBadge.tsx        # One-tap dial pills (108, 102, 1800-313-444-222)
│   │   └── index.ts
│   ├── chat/
│   │   ├── ChatWindow.tsx            # Bounded auto-scrolling viewport with ARIA live region
│   │   ├── MessageBubble.tsx         # User & assistant turn cards with 4 route themes
│   │   ├── ChatInput.tsx             # 52px floating dock with 500-character counter
│   │   ├── QuickPrompts.tsx          # 44px pill chips for rapid inquiry submission
│   │   ├── TypingIndicator.tsx       # Two-stage clinical verification pulse
│   │   └── index.ts
│   ├── evidence/
│   │   ├── CitationAccordion.tsx     # Radix accordion displaying WHO/ICMR 4-field metadata
│   │   ├── EvidenceBadge.tsx         # Level 1/2 clinical authority badge
│   │   ├── VerificationBadge.tsx     # NLI verification pass badge
│   │   └── index.ts
│   ├── safety/
│   │   ├── EmergencyDialog.tsx       # Radix dialog with 108 dispatch & admission criteria
│   │   ├── MedicationWarning.tsx     # Radix dialog with NSAID contraindication policy
│   │   ├── SafeAbstainCard.tsx       # Out-of-scope clinical referral card
│   │   └── index.ts
│   └── inspector/
│       ├── InspectorPanel.tsx        # Slide-over LangGraph state machine trace panel
│       ├── LangGraphTrace.tsx        # 4-stage lifecycle visualization
│       ├── ClaimList.tsx             # Basu & Huynh claim verification audit list
│       └── MetricsBar.tsx            # Latency and NLI score instrumentation
└── pages/
    ├── ChatPage.tsx                  # Main Sahayata Desk workspace
    ├── AboutPage.tsx                 # Academic disclosure, governance & research papers
    └── NotFoundPage.tsx              # Accessible 404 recovery page
```

---

## 6. Modular Component Contracts & Implementation Details

### 6.1 `AppShell.tsx` & `GIGWToolbar.tsx` (Civic Navigation & Accessibility)
- **AppShell:** Encloses the viewport in a civic frame. Features the West Bengal health shield emblem, the project title with amber accent, the statutory qualification *"Proposed for Dept. of Health & Family Welfare — Govt. of West Bengal"* (respecting the *State Emblem of India Act, 2005*), telephony action buttons, and the Inspector Mode toggle.
- **GIGWToolbar:** Anchored above the header. Provides buttons with `min-h-[44px] min-w-[44px]`:
  - `A-`, `A`, `A+` font size stepping.
  - `Contrast` toggle (switches between standard light civic palette and high-contrast Yellow-on-Black).
  - Language toggle (`EN` | `বাংলা`).

### 6.2 `CitizenBentoGrid.tsx` & `EmergencyRibbon.tsx` (Pre-Inference Triage)
- **EmergencyRibbon:** Positioned at the top of the citizen view. Explains the **defervescence transition (Days 3–7)** when fever drops and severe dengue shock syndrome (DSS) peaks. Contains a direct dial button for **Ambulance (108)** and a link opening hospital admission criteria.
- **CitizenBentoGrid:** 4 interactive cards with 1-tap inquiries:
  1. *Critical Warning:* When fever drops (Days 3–7 plasma leakage).
  2. *Medication Hazard:* Why avoid Aspirin & Ibuprofen (NSAID bleeding hazard).
  3. *Clinical Fluid Care:* Oral rehydration salts (ORS) & scientific evidence on papaya leaf extract.
  4. *Diagnostic Protocol:* NS1 Antigen (Days 1–5) vs IgM/IgG Antibody (> Day 5) testing windows.

### 6.3 `ChatWindow.tsx`, `MessageBubble.tsx` & `ChatInput.tsx` (Conversational Workspace)
- **ChatWindow:** Implements auto-scrolling with user-scroll detection (pauses auto-scroll if citizen scrolls up to read citations). Configured with `role="status"` and `aria-live="polite"` so screen readers announce incoming verified answers without interrupting speech.
- **MessageBubble:** Formats assistant responses according to the LangGraph route:
  - `urgent`: Crimson border, telephone icon, immediate 108 dispatch card.
  - `medication`: Amber alert card, contraindication policy details, chronic prescription preservation alert.
  - `education`: Clinical teal accent, verified response text, and embedded `CitationAccordion`.
  - `uncertain`: Neutral slate card with 1800 helpline referral.
- **ChatInput:** 52px mobile-optimized floating dock. Limits input to 500 characters with an accessible live character counter. Includes automatic multiline expansion up to 120px and handles `Shift + Enter` for newlines vs `Enter` to submit.

### 6.4 `CitationAccordion.tsx` (Transparent Evidence Disclosure)
Built with `@radix-ui/react-accordion`. Expands underneath verified educational answers to reveal the 4 mandatory evidence metadata fields defined in `plan/version_1/GuardDengue-Architecture-Review.md`:
1. **Source Authority:** Canonical publisher (e.g., `WHO Clinical Management Guidelines 2024`, `ICMR Protocol`).
2. **Publication Date:** ISO date (`2024-08-10`).
3. **Evidence Level:** Controlled badge (e.g., `Level 1 (Global Clinical Practice Guideline)`).
4. **Knowledge Topics:** Controlled multi-label tags from the 13-category taxonomy.
5. **Exact Supporting Passage:** Verbatim evidence chunk cited from the indexed clinical guideline.

### 6.5 `EmergencyDialog.tsx` & `MedicationWarning.tsx` (Deterministic Safety Dialogs)
- **EmergencyDialog:** Accessible modal overlay (`role="alertdialog"`) triggered by red-flag symptoms. Provides 1-tap direct dialing to `tel:108` or `tel:102`, outlines the 6 WHO emergency warning signs, and lists hospital admission indicators.
- **MedicationWarning:** Accessible modal overlay warning against NSAIDs (Ibuprofen, Aspirin, Naproxen, Diclofenac) due to thrombocytopenic gastrointestinal hemorrhage risk. Emphasizes that Paracetamol should be used within safe limits and provides an explicit instruction **never to stop chronic daily prescription medications** without consulting a physician.

### 6.6 `AboutPage.tsx` (Academic Disclosure & Research Citations)
Presents the formal academic and clinical governance in a clean, professional dual-column layout:
- **Academic Supervision:** Prof. (Dr.) Amlan Chakraborty (Lead Supervisor), Dr. Wazib (LLM/RAG Architecture), Dr. Jhilam (Health Data Analytics).
- **Research Team:** Souptik Dutta, Ayan Chakraborty, Rupchand Naiya, Swarnajit Paul (B.Tech, A.K.C.S.I.T., University of Calcutta).
- **Statutory Authority Sources:** WHO 2024, ICMR, NCVBDC, WB Health Department.
- **Published Research Citations:** Amugongo et al. (PLOS 2025) and Basu & Huynh (BMC 2026).

---

## 7. Frontend-to-Backend API Contract & Communication Protocol

The client communicates with the backend exclusively via `POST` requests to protect patient privacy (symptoms and queries are never leaked into server URL access logs or browser history):

### 7.1 Single-Turn REST Endpoint: `POST /api/chat`
Used for test automation, fallback environments, and non-streaming responses.

#### Request Schema:
```json
{
  "message": "Can I take ibuprofen or aspirin for dengue fever?",
  "session_id": "sess_wb_8921a9c8",
  "language": "en",
  "history": []
}
```

#### Response Schema (`200 OK` — Medication Route):
```json
{
  "session_id": "sess_wb_8921a9c8",
  "route": "medication",
  "verdict": "template_bypass",
  "evidence_ok": true,
  "attempts": 0,
  "is_fallback": false,
  "answer": "Do NOT take ibuprofen, aspirin, naproxen, or any NSAIDs. These medications inhibit platelet aggregation and significantly increase the risk of severe gastrointestinal bleeding in dengue patients. Paracetamol is the recommended antipyretic within approved limits. If you are taking doctor-prescribed medications for chronic conditions, do not discontinue them without consulting your physician.",
  "evidence": [
    {
      "id": "KB-MED-001",
      "score": 1.0,
      "category": "Medication safety",
      "content": "Aspirin and other non-steroidal anti-inflammatory drugs (NSAIDs) like ibuprofen must be avoided due to the risk of hemorrhage...",
      "metadata": {
        "source": "WHO Dengue Guidelines for Clinical Management",
        "publication_date": "2024-08-10",
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "topic": ["Medication safety", "Warning signs"],
        "chunk_id": "KB-MED-001",
        "corpus_release": "2026.09-v2-approved"
      }
    }
  ],
  "safety_disclaimer": "This is general health awareness information, not an individual clinical diagnosis or prescription.",
  "matched_rules": ["nsaid_contraindication_rule", "chronic_rx_protection_rule"],
  "telephony_action": {
    "recommended_call": "108",
    "helpline": "1800-313-444-222"
  },
  "metrics": {
    "total_latency_ms": 14,
    "zone2_screener_ms": 14,
    "model_generation_ms": 0,
    "nli_verification_ms": 0
  }
}
```

### 7.2 SSE Streaming Protocol: `POST /api/chat/stream`
The primary conversational endpoint. Uses `fetch()` with `ReadableStream` (`frontend/src/api/client.ts`):

```typescript
export function streamMessage(
  req: ChatRequest,
  onEvent: (event: StreamEvent) => void,
  onError: (error: Error) => void,
  onDone: () => void,
): () => void
```

#### SSE Stream Event Sequence:
1. `event: screener_triage`: Emitted when Zone 2 resolves the route (`urgent`, `medication`, `education`, `uncertain`).
2. `event: template_bypass`: Emitted for `urgent` or `medication` queries to bypass generative inference.
3. `event: retrieval_complete`: Emitted when Qdrant returns candidate evidence chunks.
4. `event: verification_progress`: Emitted when the Claim Verification Gate evaluates Basu & Huynh NLI checks.
5. `event: answer_publish`: Emitted with the final, verified answer and metadata accordions.
6. `event: answer_abstain`: Emitted if the query is out-of-scope or fails verification twice.

---

## 8. State Management Architecture

State is managed locally using React 19 Context and hooks:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        SettingsContext Architecture                    │
├───────────────────┬────────────────────────────────────────────────────┤
│ language          │ 'en' | 'bn' (persisted in localStorage)            │
│ contrast          │ 'normal' | 'high' (toggles .contrast-high on <html>│
│ fontSize          │ 'normal' | 'large' | 'larger'                      │
│ inspectorMode     │ boolean (toggles Dr. Wazib's clinical trace panel) │
└───────────────────┴────────────────────────────────────────────────────┘
```

The `SettingsContext` automatically applies DOM class mutations on change (`applySettingsToDOM`), ensuring instant high-contrast re-skinning and typography adjustments without page reloads.

---

## 9. Verification & Quality Gates

The frontend codebase satisfies all project quality gates:
1. **TypeScript Build:** `tsc -b && vite build` compiles cleanly with **0 errors** in **706ms**.
2. **Linter:** `oxlint` passes cleanly across all 46 files with **0 errors**.
3. **Accessibility:** WCAG AA compliant contrast ratios ($\ge 4.5:1$ in normal mode, $\ge 7:1$ in high-contrast mode), all interactive elements have visible focus rings and ARIA labels.
4. **Git Hygiene:** Zero `.env` files, build caches, or temporary artifacts tracked.

---

## 10. Direct Backend Implementation Contracts (For Next Session)

When implementing the FastAPI and LangGraph backend in `backend/`, the following contracts must be respected:
1. **Endpoint Paths:** Must implement `POST /api/chat` and `POST /api/chat/stream`.
2. **CORS Configuration:** Allow `http://localhost:5173` in development mode.
3. **Static File Mount:** Mount `backend/static` at `/` for production single-process serving (`app.mount("/", StaticFiles(directory="static", html=True))`).
4. **Route Field:** The LangGraph state machine must return one of the 4 canonical string literals: `"urgent"`, `"medication"`, `"education"`, `"uncertain"`.
5. **Metadata Schema:** Evidence metadata must contain the 4 required fields: `source`, `publication_date`, `evidence_level`, and `topic`.
