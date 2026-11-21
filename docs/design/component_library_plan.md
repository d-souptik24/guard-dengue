# GuardDengue: React Component Library & Implementation Roadmap

> **Document Type:** Engineering Component Architecture & Code Implementation Roadmap  
> **Tech Stack:** Vite 8 + React 19 + TypeScript 7 + Tailwind CSS v4 + Radix UI / shadcn/ui + UX4G Patterns  
> **Status:** REVISED IMPLEMENTATION ROADMAP (PENDING FINAL REVIEW)  

---

## 1. Component Architecture & Library Strategy

### 1.1 The Hybrid Architectural Choice
Rather than importing a rigid, black-box npm component suite (which creates vendor lock-in and breaks during framework upgrades), GuardDengue uses the **Copy-Paste Component Model**:
- **Radix UI Primitives (Headless):** Powers all interactive behaviors (Dialogs, Accordions, Tooltips, Selects, Switches) with 100% WAI-ARIA compliance.
- **shadcn/ui Pattern:** Component source files live directly in `src/components/ui/`, giving us total control over class styling, Tailwind v4 tokens, and custom state logic.
- **UX4G 2.0 Civic Patterns:** Reusable Indian Government public service molecules (accessible bilingual headers, emergency telephony banners, citizen bento action tiles, GIGW footers).

---

## 2. Component Refactoring & Construction Inventory

```
frontend/src/components/
├── layout/
│   ├── GIGWToolbar.tsx         # [NEW] Top GIGW accessibility strip (A-, A+, Contrast, Lang)
│   ├── AppShell.tsx            # [REFACTOR] WB Health saffron masthead & custom health shield
│   └── GovFooter.tsx           # [NEW] Authentic wb.gov.in-style light grey centered footer
│
├── citizen/
│   ├── CitizenBentoGrid.tsx    # [NEW] Saffron/Ochre action blocks (Symptoms, Meds, Labs)
│   ├── EmergencyRibbon.tsx     # [NEW] Full-width integrated defervescence alert
│   └── TelephonyBadge.tsx      # [NEW] Click-to-dial 108 / 102 & 1800-313-444-222 hub
│
├── chat/
│   ├── ChatWindow.tsx          # [REFACTOR] Clean, non-slop conversation container
│   ├── MessageBubble.tsx       # [REFACTOR] Deep slate & warm amber response cards
│   ├── ChatInput.tsx           # [REFACTOR] 52px accessible input dock with clear button
│   ├── QuickPrompts.tsx        # [REFACTOR] Saffron pill suggestions
│   └── TypingIndicator.tsx     # [POLISH] Reassuring "Verifying Clinical Evidence..." pulse
│
├── safety/
│   ├── MedicationWarning.tsx   # [IMPLEMENT] Radix Dialog: NSAID contraindication explanation
│   ├── EmergencyDialog.tsx     # [IMPLEMENT] High-urgency hospital referral modal
│   └── SafeAbstainCard.tsx     # [IMPLEMENT] Calm, humble out-of-scope abstention card
│
├── evidence/
│   ├── EvidenceBadge.tsx       # [POLISH] Topic chip + Level 1/2 indicator
│   ├── CitationAccordion.tsx   # [REFACTOR] Expandable accordion with WHO/ICMR source details
│   └── VerificationBadge.tsx   # [POLISH] Verified Source Citation indicator
│
└── inspector/
    ├── InspectorPanel.tsx      # [REFACTOR] Dark-slate supervisor drawer for Dr. Wazib
    ├── LangGraphTrace.tsx      # [POLISH] Animated state machine nodes (4 routes)
    ├── MetricsBar.tsx          # [POLISH] Telemetry & deployment stage footprint (Colab T4 vs Server)
    └── ClaimList.tsx           # [POLISH] Input/Context/Fact conflict scorecard
```

---

## 3. Detailed Component Refactoring Specifications

### 3.1 `GIGWToolbar.tsx` (New Component)
- **Position:** Anchored at the very top of the viewport ($34\text{px}$ height).
- **Features:**
  - "Skip to main content" link for keyboard users.
  - Font scaling: Dispatches `document.documentElement.style.fontSize = "18px"` on `A+`.
  - High Contrast: Toggles `[data-contrast="high"]` on `<html>`.
  - Language: Clean pill switch between `English` and `বাংলা`.

### 3.2 `AppShell.tsx` (Refactored Masthead)
- **Visuals:** Warm saffron gradient header with deep ochre curved bottom border inspired by `wbhealth.gov.in`.
- **Left:** Custom GuardDengue Health Shield SVG + Bilingual Department Typography:
  - *স্বাস্থ্য ও পরিবার কল্যাণ দপ্তর — পশ্চিমবঙ্গ সরকার*
  - *Department of Health & Family Welfare — Government of West Bengal*
  - *Academic Health-Awareness Prototype — Proposed for Dept. of Health & Family Welfare, Govt. of West Bengal*
- **Right:**
  - One-tap telephone dialer: `🚑 108 / 102` (Ambulance) & `📞 1800-313-444-222`.
  - Discreet "Clinical Inspector" button for Dr. Wazib and examiners.

### 3.3 `CitizenBentoGrid.tsx` (New Component)
- Provides immediate 1-tap answers for the most common citizen questions, preventing cognitive overload:
  - **Tile 1 (Golden Ochre `#92400E`):** *জ্বর কমার সময় কেন সবচেয়ে বিপজ্জনক?* (Defervescence phase explained).
  - **Tile 2 (Action Amber `#B45309`):** *আইবুপ্রোফেন বা অ্যাসপিরিন কেন ক্ষতিকর?* (NSAID bleeding hazard & chronic Rx caution).
  - **Tile 3 (Teal `#0F766E`):** *পেঁপে পাতা বনাম ওআরএস (ORS) এর সত্যতা* (Myth busting & hydration).
  - **Tile 4 (Blue `#1E3A8A`):** *রক্তের পরীক্ষা: NS1 নাকি IgM?* (Diagnostic timing guide).

### 3.4 `ChatWindow.tsx` & `MessageBubble.tsx` (Refactored)
- **Eliminates AI Slop:** Removes bulky full-screen pink cards, replacing them with:
  - **User Turn:** Right-aligned warm amber badge with crisp white text.
  - **Assistant Turn:** Left-aligned clean white card with subtle slate border and Swasthya Bhawan verified badge.
  - **Staged Verification Loader:** Reassuring pulse (*"Checking verified guidelines..."* $\rightarrow$ *"Verifying clinical safety rules..."*).
  - **Evidence Accordion:** Clean dropdown disclosing source document, author, date, and clinical evidence grade.

---

## 4. Cache-Busting Favicon & Tab Metadata Resolution

### 4.1 Root Cause of Current Tab Icon Glitch:
The browser is currently displaying a cached red/orange stylized `α` icon from a previous project on `localhost:5173`. This occurs because `index.html` references `/vite.svg` without explicit cache-busting query strings or dedicated ICO fallbacks.

### 4.2 Concrete Remediation Steps:
1. **Asset Creation:**
   - Create `frontend/public/guarddengue_wb_emblem.svg`: An official vector graphic displaying the GuardDengue health shield inspired by `wbhealth.gov.in`'s authentic teal heart-and-cross motif (strictly avoiding prohibited statutory insignia or traditional medical staff symbols).
   - Create `frontend/public/favicon.ico`: Multi-layer icon file containing 16x16, 32x32, and 48x48 pixel representations.
2. **HTML Update (`frontend/index.html`):**
   ```html
   <link rel="icon" type="image/svg+xml" href="/guarddengue_wb_emblem.svg?v=2.1" />
   <link rel="alternate icon" href="/favicon.ico?v=2.1" />
   <title>পশ্চিমবঙ্গ স্বাস্থ্য — GuardDengue | Health & Family Welfare Department</title>
   ```
3. **PWA / Browser Theme Color:**
   ```html
   <meta name="theme-color" content="#B45309" />
   ```

---

## 5. Execution Phasing (Once Approved)

```
Phase 1: Brand Assets & Tokens
• Generate official GuardDengue SVG/ICO favicon (resolve alpha logo bug)
• Update index.html with official metadata and cache-busting tags
• Inject official Tailwind v4 tokens into index.css

Phase 2: Structural Components
• Build GIGWToolbar and GovFooter
• Reconstruct AppShell with authentic West Bengal Health saffron masthead
• Build CitizenBentoGrid and integrated EmergencyRibbon

Phase 3: Conversational Workspace
• Reconstruct ChatWindow, MessageBubble, and ChatInput with 44px targets
• Refactor CitationAccordion to display WHO/ICMR Level 1/2 metadata
• Wire MedicationWarning and EmergencyDialog modals

Phase 4: Clinical Inspector Polish
• Polish InspectorPanel drawer styling to match Dr. Wazib's audit needs
• Connect live SSE streaming (POST /api/chat/stream) and LangGraph state telemetry

Phase 5: Verification & Accessibility Audit
• Verify WCAG 2.1 AA color contrast across all viewports
• Verify 0 console errors, 0 build warnings, and test with screen reader
```
