# GuardDengue: Brand Guidelines & Visual Identity (Moodboard)

> **Document Type:** Visual Identity, Civic Branding, Typography & Moodboard Standards  
> **Brand Context:** Department of Health & Family Welfare, Government of West Bengal  
> **Status:** REVISED BRAND IDENTITY BASELINE (PENDING FINAL REVIEW)  

---

## 1. Brand Mission & Civic Personality

GuardDengue is not an entertainment chatbot or a commercial consumer app. It is an **Academic Public Health-Awareness Prototype** proposed for the **Department of Health & Family Welfare, Government of West Bengal**. Its visual identity must evoke:
- **Authority & Trust:** Instilling immediate confidence through recognized civic typography and transparent academic attribution.
- **Compassion & Calm:** Lowering panic during an acute health crisis or seasonal dengue outbreak.
- **Scientific Grounding:** Visualizing verified clinical evidence with academic transparency.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        BRAND PERSONALITY MATRIX                        │
├──────────────────────┬─────────────────────────────────────────────────┤
│ We Are               │ We Are NOT                                      │
├──────────────────────┼─────────────────────────────────────────────────┤
│ Authoritative & Civic│ Bureaucratic, sterile, or indifferent           │
│ Reassuring & Caring  │ Alarming, sensational, or panic-inducing        │
│ Scientifically Exact │ Speculative, diagnostic, or prescribing         │
│ Clean & Approachable │ Generic AI-slop with floating neon widgets      │
│ Deeply Bilingual     │ English-centric with broken Bengali translations│
└──────────────────────┴─────────────────────────────────────────────────┘
```

---

## 2. Moodboard & Color World

The color system reflects the physical environment of West Bengal's civic architecture, heritage buildings, and public health portals (`wbhealth.gov.in` and `wb.gov.in`):

```
┌────────────────────────────────────────────────────────────────────────┐
│                       GUARDDENGUE MOODBOARD WORLD                      │
│                                                                        │
│  [Warm Saffron Masthead]       ──► [Deep Heritage Ochre Accents]       │
│  [Swasthya Bhawan White/Teal]  ──► [Golden Amber Administrative Tiles] │
│  [Civic Blue Telephony Hub]    ──► [Calm Linen Public Health Canvas]   │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 The Official Color Palette

| Token Name | Hex Code | Role in UI | Emotional Association |
| :--- | :--- | :--- | :--- |
| **`wb-amber-action`**  | `#B45309` | Primary action buttons (white text safe: 5.02:1) | Warmth, energy, civic vigilance |
| **`wb-saffron-highlight`**| `#F59E0B`| Service ribbons, language pill (dark text only) | Bengal golden saffron, accessibility |
| **`wb-ochre-heritage`** | `#92400E` | Administrative headers, bento card backgrounds | Heritage brick, stability, authority |
| **`wb-blue-telephony`** | `#1E3A8A` | 108 / 102 Ambulance and Swasthya Helpline tiles | Lifeline, emergency reliability |
| **`wb-crimson-emergency`**| `#B91C1C`| Emergency warning signs (Days 3–7 defervescence)| Critical life-safety warning |
| **`wb-teal-evidence`**  | `#0F766E` | WHO/NCVBDC citation badges, verified checkmarks | Clinical evidence, scientific rigor |
| **`wb-canvas`**         | `#FDFBF7` | Main page background (eliminates harsh white) | Warm civic linen, visual comfort |
| **`wb-text-main`**      | `#0F172A` | Primary typography and headings | Deep slate ink, maximum legibility |

---

## 3. Emblems, Badges & Iconography

### 3.1 Transparent Academic & Departmental Masthead
In compliance with the *State Emblem of India (Prohibition of Improper Use) Act, 2005*, the academic prototype does not display restricted statutory insignia. Instead, it pairs official departmental titles with a clear academic research credit:
```
পশ্চিমবঙ্গ সরকার — স্বাস্থ্য ও পরিবার কল্যাণ দপ্তর
Department of Health & Family Welfare — Government of West Bengal
Academic Health-Awareness Prototype — Proposed for Dept. of Health & Family Welfare, Govt. of West Bengal
```

### 3.2 GuardDengue Health Shield Identifier
- A bespoke vector shield inspired by `wbhealth.gov.in`'s authentic teal heart-and-cross motif:
  - An outer protective shield in warm amber (`#B45309`).
  - An inner heart-and-cross health emblem in teal (`#0F766E`).
  - A clean bilingual title: **GuardDengue / গার্ডডেঙ্গু** with the subtitle: *Evidence-Grounded Dengue Health Awareness*.

### 3.3 Iconography Rules
- **Rule 1 (Zero Emoji as UI Markers):** Never use consumer emojis (🚨, 🦟, 💊, 🩸) as structural UI icons. Emojis render inconsistently across Android/Windows/iOS and diminish institutional gravitas.
- **Rule 2 (Unified Line Icon Family):** Use **Lucide React** line icons exclusively, styled in `currentColor` with a consistent `1.75px` stroke width.
  - Emergency: `<AlertOctagon className="w-5 h-5 text-red-700" />`
  - Verification: `<ShieldCheck className="w-5 h-5 text-teal-700" />`
  - Telephony: `<PhoneCall className="w-4 h-4 text-white" />`
  - Evidence: `<FileText className="w-4 h-4 text-slate-700" />`

---

## 4. Typography & Bilingual Type System

Typography is engineered to ensure seamless parity between English and Bengali scripts:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        BILINGUAL FONT STACK                            │
├─────────────────────┬──────────────────────────────────────────────────┤
│ English Body & UI   │ Inter (Sans-Serif, Variable: 300–800)            │
│ Bengali Body & UI   │ Hind Siliguri (হিন্দ শিলিগুড়ি, Google Fonts)   │
│ Monospace / Trace   │ JetBrains Mono / Fira Code (Inspector Panel only)│
└─────────────────────┴──────────────────────────────────────────────────┘
```

### 4.1 Type Scale & Hierarchy

| Semantic Level | Font Size | Line Height | Weight | Tracking | Intended Use |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display 1** | $32\text{px}$ (`2rem`) | $1.2$ (`leading-tight`) | 700 Bold | `-0.02em` | Portal Hero Title |
| **Heading 2** | $24\text{px}$ (`1.5rem`)| $1.3$ (`leading-snug`) | 600 SemiBold| `-0.01em` | Section / Bento Titles |
| **Heading 3** | $18\text{px}$ (`1.125rem`)| $1.4$ | 600 SemiBold| `normal` | Message Header / Modal Title |
| **Body (Default)**| $16\text{px}$ (`1rem`) | $1.6$ (`leading-relaxed`)| 400 Regular | `normal` | Educational Guidance Prose |
| **Bengali Body** | $16\text{px}$ (`1rem`) | $1.75$ (`leading-loose`)| 400/500 | `normal` | Bengali sentences require extra leading |
| **Caption / Tag**| $12\text{px}$ (`0.75rem`)| $1.4$ | 500 Medium | `0.02em` | Citations, Timestamps, Sources |

---

## 5. Imagery & Asset Guidelines

1. **Integrated Header Composition:**
   - Instead of a standalone hero photograph pushing the workspace below the fold, the header incorporates warm saffron-to-ochre gradients with subtle geometric lines directly derived from `wbhealth.gov.in`.
2. **Clinical Infographics:**
   - Only authoritative diagrams extracted via the **Docling pipeline** (e.g., WHO Clinical Management Algorithm, ICMR laboratory testing timeline) are permitted.
3. **STRICT PROHIBITION OF AI-SLOP CARTOON ART:**
   - Do **not** use AI-generated cartoon mosquitoes, stylized anime doctors, or generic 3D glossy characters. Every graphical element must reflect official public health dignity.
