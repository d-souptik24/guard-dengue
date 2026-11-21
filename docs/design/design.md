# GuardDengue: Master Design System & UI/UX Specification

> **Document Type:** Master Design System, Visual Philosophy & UI/UX Blueprint  
> **Target Audience:** Department of Health & Family Welfare (Government of West Bengal), Dr. Wazib (Supervisor), Dr. Jhilam, Engineering Team  
> **Status:** REVISED DESIGN BASELINE (PENDING FINAL REVIEW)  
> **Compliance Standard:** UX4G 2.0 (User Experience for Government) & GIGW 3.0 (Guidelines for Indian Government Websites)  

---

## 1. Executive Summary & Root-Cause Diagnosis

### 1.1 Why the Previous Prototype Failed ("The AI Slop Problem")
The initial frontend prototype suffered from several systemic design deficiencies characteristic of uncurated AI-generated Tailwind templates:
1. **Uncalibrated Color Saturation:** Oversaturated, pastel-pink/red alerts dominated the screen unconditionally, inducing anxiety before the user had typed a query.
2. **Disconnected Visual Hierarchy:** Floating rounded cards lacked spatial anchoring, giving the impression of an ungrounded demo rather than an official civic portal.
3. **Developer Clutter:** Debug tags (`SLM V2`, `ZERO-LATENCY RULE`, `Zone 2 Screener`) were exposed directly in the citizen's primary reading path.
4. **Lack of Institutional Gravitas & Legal Boundary:** Absence of authentic West Bengal Government identity elements, coupled with unverified portal attributions.
5. **Asset Drift:** Browser tab displayed a cached logo (`α`) from an unrelated project due to missing cache-busted, dedicated government icons.

### 1.2 The New Paradigm: Authentic West Bengal e-Governance
GuardDengue is redesigned to match the visual language and user expectations of authentic West Bengal Government health portals, specifically **`wbhealth.gov.in`** and **`wb.gov.in`**:
- **Warm, Civic & Reassuring Palette:** Transition from cold clinical blues and alarming neon reds to the **West Bengal Civic Saffron, Golden Amber, Deep Heritage Ochre, and Warm Linen Canvas**.
- **Transparent Academic Governance:** Explicitly labeled as an *"Academic Health-Awareness Prototype — Proposed for Dept. of Health & Family Welfare, Govt. of West Bengal"* to strictly respect the *State Emblem of India (Prohibition of Improper Use) Act, 2005*.
- **Dual-Audience Architecture:** 
  - **Citizens:** A clean, accessible, informal, and deeply helpful public health desk (**"পশ্চিমবঙ্গ স্বাস্থ্য ডেঙ্গু সহায়তা ডেস্ক" / West Bengal Swasthya Dengue Sahayata Desk**).
  - **Academic Supervisors & Examiners (Dr. Wazib / Dr. Jhilam):** A discreet, high-utility **Clinical Trace Inspector** accessible via a dedicated administrative toggle.

---

## 2. Reference Portal Alignment (`wbhealth.gov.in` & `wb.gov.in`)

Based on empirical analysis of the official state health portals:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        WEST BENGAL GOV PORTAL DESIGN DNA                               │
├──────────────────────────┬────────────────────────────┬────────────────────────────────┤
│ Reference Portal         │ Observed UI Patterns       │ GuardDengue Adaptation         │
├──────────────────────────┼────────────────────────────┼────────────────────────────────┤
│ wbhealth.gov.in          │ • Warm Saffron-Gradient    │ Authentic saffron masthead with│
│ (Dept of Health &        │   header with deep ochre   │ deep ochre curved bottom edge. │
│  Family Welfare)         │   curved bottom edge       │                                │
│                          │ • Top-right skip, search,  │ Standardized bilingual and     │
│                          │   accessibility & অ/A icons│ accessibility controls.        │
│                          │ • Deep ochre rounded cards │ Civic bento quick-action cards.│
│                          │ • Teal heart-and-cross icon│ Custom GuardDengue shield      │
│                          │ • Floating right-edge call │ Quick-dial 108 / 102 ambulance │
│                          │   button                   │ and state helpline button.     │
├──────────────────────────┼────────────────────────────┼────────────────────────────────┤
│ wb.gov.in                │ • Light neutral grey top   │ Standard GIGW toolbar with     │
│ (State Portal)           │   accessibility strip      │ A-, A, A+ text scalers.        │
│                          │ • Light grey centered      │ Clean, centered pipe-separated │
│                          │   pipe-separated footer    │ footer with legal disclaimers. │
└──────────────────────────┴────────────────────────────┴────────────────────────────────┘
```

---

## 3. Core Design Principles

1. **Compassionate Civic Presence (Panic Reduction):**
   - Dengue fever creates severe household panic, especially when fever drops during the critical phase (Days 3–7) or when platelet counts decline.
   - The UI projects calm authority. Urgent medical warnings are highlighted with clear crimson markers (`#B91C1C`), but everyday health awareness uses warm, supportive tones.
2. **Informal, Citizen-First Plain Language:**
   - Avoid impenetrable medical jargon. A citizen asking *"আমার বাচ্চার জ্বর, প্যারাসিটামল কত দেব?"* receives clear, warm guidance refusing direct dosage calculation while explaining safe pediatric limits and directing to a pediatrician.
3. **One Radius, One Personality (Anti-Slop Craft Rule):**
   - Standard container radius: `rounded-xl` ($12\text{px}$).
   - Standard inner element radius: `rounded-lg` ($8\text{px}$) for buttons, textareas, and interactive controls.
4. **Bilingual Parity (English & বাংলা):**
   - English and Bengali enjoy equal design dignity. Layouts do not break or truncate when toggled to Bengali script (`Hind Siliguri`).
5. **Separation of Evidence from Diagnostics:**
   - Every educational claim displays an expandable **Verified Source Citation** (`WHO 2024`, `NCVBDC 2025`, `Level 1 Evidence`), emphasizing that GuardDengue is an evidence retrieval engine, not a prescribing doctor.
6. **Immediate Above-the-Fold Workspace:**
   - To eliminate visual obstruction on citizen devices, the top banner is integrated compactly into the masthead without a separate hero image, ensuring the conversational Sahayata Desk is immediately interactive upon page load.

---

## 4. Layout Architecture & Anatomy

The interface is structured into five distinct anatomical layers, maintaining the workspace above the fold:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. GIGW Accessibility Strip: Font Size [A- A A+] | Contrast | Lang [EN|বাংলা]│
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. WB Health Saffron Masthead: Custom Teal Heart-and-Cross Health Shield   │
│    Department of Health & Family Welfare | Academic Prototype Subtitle      │
│    Quick Helpline Action: 📞 1800-313-444-222 | 🚑 108 / 102                │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Integrated Emergency Advisory Ribbon: Critical Defervescence Warning     │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Primary Civic Workspace (Two-Column Responsive Grid — Above-the-Fold)    │
│    ┌───────────────────────────────────┬────────────────────────────────┐   │
│    │ Citizen Action Bento Grid         │ Swasthya Sahayata Desk         │   │
│    │ • Warning Signs When Fever Drops  │ (Evidence-Grounded Chat Window)│   │
│    │ • Why Avoid Aspirin/Ibuprofen     │ • User message bubble          │   │
│    │ • Hydration & Platelet Facts      │ • Staged Verification Loader   │   │
│    │ • Testing Guidelines (NS1 vs IgM) │ • Verified answer + Citations  │   │
│    │ • Swasthya Kendra Directory       │ • Anchored 52px input dock     │   │
│    └───────────────────────────────────┴────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│ 5. Official Light-Grey Footer: Centered pipe-separated links & disclaimer    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.1 Layer Breakdown

#### Layer 1: GIGW Accessibility & Language Toolbar
- Background: Light neutral grey (`#F1F5F9`) with dark text (`#0F172A`).
- Controls:
  - `Skip to main content` (Screen-reader accessible).
  - Font size toggle: `A-` (Small, 14px), `A` (Default, 16px), `A+` (Large, 18px).
  - Contrast mode: `Normal` / `High Contrast` (`[data-contrast="high"]` theme override).
  - Language toggle: `English` | `বাংলা` (`language: "en" | "bn"` stateful toggle).

#### Layer 2: West Bengal Health Saffron Masthead
- Visuals: Warm saffron gradient (`from-amber-600 to-amber-700`) with deep ochre curved bottom border inspired by `wbhealth.gov.in`.
- Left: **Custom GuardDengue Health Shield** (stylized teal heart-and-cross motif in `#0F766E` and `#B45309`) with bilingual typography:
  - English: **Department of Health & Family Welfare — Government of West Bengal**
  - Bengali: **স্বাস্থ্য ও পরিবার কল্যাণ দপ্তর — পশ্চিমবঙ্গ সরকার**
  - Subtitle: *Academic Health-Awareness Prototype — Proposed for Dept. of Health & Family Welfare, Govt. of West Bengal*
- Right:
  - `Swasthya Bhawan Helpline: 1800-313-444-222`
  - `Ambulance: 108 / 102` (One-tap emergency dialer).
  - `Clinical Inspector Toggle` (Discreet audit view for Dr. Wazib / Examiners).

#### Layer 3: Integrated Emergency Advisory Ribbon
- A high-visibility, full-width amber/crimson ribbon:
  > **জরুরী সতর্কতা / Critical Advisory:** ডেঙ্গু জ্বরে জ্বর কমার সময় (Days 3–7) সবচেয়ে বিপজ্জনক। পেটে তীব্র ব্যথা, বারবার বমি, মাড়ি দিয়ে রক্ত পড়া দেখা দিলে অবিলম্বে হাসপাতালে যান।
- Includes direct click-to-call `108` button.

#### Layer 4: Primary Civic Workspace (Above-the-Fold)
- **Left Column (Citizen Action Bento Grid):**
  - **Card 1: Defervescence Warning Signs** (Explaining the 24–48hr danger period after fever leaves).
  - **Card 2: Medication Precautions** (Distinguishing OTC NSAID avoidance from prescribed medication continuation).
  - **Card 3: Hydration & Platelet Reality** (Busting papaya leaf myths and explaining ORS fluid resuscitation).
  - **Card 4: Testing & Laboratory Guidelines** (Timeline comparison: NS1 Antigen Days 1–5 vs IgM/IgG > Day 5).
- **Right Column (Swasthya Dengue Sahayata Desk):**
  - Clean conversation stream.
  - **Staged Verification Loader:** Reassuring pulse (*"Checking verified guidelines..."* $\rightarrow$ *"Verifying clinical safety rules..."*).
  - **Input Dock:** Symmetrically centered $52\text{px}$ touch-target input with Bengali typing support and clear action button.

#### Layer 5: Official Light-Grey Footer
- Modeled directly on `wb.gov.in`:
  - Centered pipe-separated links: *Home | About The Portal | Site Map | Copyright Policy | Terms Of Use | Feedback | Help | Contact Us | Downloads*.
  - Statutory Medical Disclaimer: *"GuardDengue is an academic health-education prototype and does not provide medical diagnoses or prescriptions. For medical emergencies, call 108 / 102 or contact Swasthya Bhawan at 1800-313-444-222."*
  - Technical Credits: *"Developed as a B.Tech. IT Minor Project in collaboration with Academic Research Supervisors."*

---

## 5. Explicit LangGraph UI States

The conversational desk renders four distinct, mutually exclusive outcome cards:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH UI OUTCOME CARDS                      │
├─────────────────────┬──────────────────────────────────────────────────┤
│ Route Outcome       │ Visual Styling & Clinical Behavior               │
├─────────────────────┼──────────────────────────────────────────────────┤
│ 1. urgent           │ Crimson Card (#B91C1C border, #FEF2F2 bg):       │
│                     │ Immediate zero-RAG escalation. Highlights shock  │
│                     │ warning signs with direct click-to-call 108.    │
├─────────────────────┼──────────────────────────────────────────────────┤
│ 2. medication       │ Amber Policy Card (#B45309 border, #FFFBEB bg):  │
│                     │ Distinguishes OTC NSAID avoidance (aspirin,      │
│                     │ ibuprofen) while explicitly warning NOT to stop  │
│                     │ doctor-prescribed medications without consulting.│
├─────────────────────┼──────────────────────────────────────────────────┤
│ 3. education        │ Pure White Card (#FFFFFF surface, #E2E8F0 border)│
│                     │ Grounded educational guidance with collapsible   │
│                     │ 4-field metadata Evidence Accordion.             │
├─────────────────────┼──────────────────────────────────────────────────┤
│ 4. uncertain /      │ Neutral Slate Card (#64748B border, #F8FAFC bg): │
│    abstain          │ Calm, humble abstention directing citizens to    │
│                     │ official state portals or medical professionals. │
└─────────────────────┴──────────────────────────────────────────────────┘
```

---

## 6. Visual Theme & Color Palette

```
                  GUARDDENGUE OFFICIAL CIVIC PALETTE
                  
   #B45309               #F59E0B               #92400E               #1E3A8A
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Deep Amber  │      │ Saffron Gold │      │ Bengal Ochre │      │ Citizen Blue │
│ (White Text) │      │  (Dark Text) │      │ (Bento/Card) │      │  (Helpline)  │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
   
   #B91C1C               #0F766E               #FDFBF7               #0F172A
┌──────────────┐      ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Emergency   │      │   Evidence   │      │ Civic Linen  │      │  Slate Ink   │
│   Crimson    │      │     Teal     │      │ (Background) │      │ (Typography) │
└──────────────┘      └──────────────┘      └──────────────┘      └──────────────┘
```

1. **`--wb-amber-action: #B45309`**: Primary civic brand color for white-text buttons, active tabs, and primary borders ($5.02:1$ contrast against white).
2. **`--wb-saffron-highlight: #F59E0B`**: Warm interactive highlight, reserved for dark-ink text (`#0F172A`, $8.31:1$) or decorative borders.
3. **`--wb-ochre-heritage: #92400E`**: Deep administrative headers and prominent section titles ($7.09:1$ contrast against white).
4. **`--wb-blue-telephony: #1E3A8A`**: Civic helpline tiles and institutional links ($10.36:1$ contrast against white).
5. **`--wb-crimson-emergency: #B91C1C`**: Emergency triage red-flag alerts ($5.91:1$ on `#FEF2F2` background, $6.47:1$ with white text).
6. **`--wb-teal-evidence: #0F766E`**: Verified clinical evidence tags and source citation badges ($5.25:1$ on `#F0FDFA`).
7. **`--wb-canvas: #FDFBF7`**: Warm civic linen/cream background ($17.27:1$ contrast against `#0F172A` text).
8. **`--wb-text-main: #0F172A`**: Deep slate ink for maximum WCAG AA/AAA readability.

---

## 7. Favicon & Identity Correction Plan

To eliminate the cached alpha (`α`) logo:
1. Generate an official, cache-busted vector asset: `frontend/public/guarddengue_wb_emblem.svg` featuring the teal heart-and-cross health shield inspired by `wbhealth.gov.in`.
2. Generate `frontend/public/favicon.ico` with multi-resolution bitmaps (16x16, 32x32, 48x48).
3. Update `frontend/index.html`:
   ```html
   <link rel="icon" type="image/svg+xml" href="/guarddengue_wb_emblem.svg?v=2.1" />
   <link rel="alternate icon" href="/favicon.ico?v=2.1" />
   <meta name="theme-color" content="#B45309" />
   ```
