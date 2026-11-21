# GuardDengue: Accessibility (a11y) & UX4G Compliance Checklist

> **Document Type:** Mandatory Accessibility & Government Web Standards Matrix  
> **Standards:** WCAG 2.1 Level AA, UX4G 2.0 (User Experience for Government), GIGW 3.0 (Guidelines for Indian Government Websites)  
> **Status:** REVISED ACCESSIBILITY SPECIFICATION (PENDING FINAL REVIEW)  

---

## 1. Compliance Mandate

Under the **Rights of Persons with Disabilities Act (RPwD Act, 2016)** and **MeitY / GIGW Guidelines**, all government-affiliated digital platforms in India must meet **WCAG 2.1 Level AA** standards. GuardDengue adheres strictly to these requirements to guarantee that every citizen—regardless of age, visual acuity, physical disability, or digital literacy—can access life-saving dengue awareness.

---

## 2. Accessibility Verification Matrix

### 2.1 Perceivable (Sensory Access)

| Checklist Item | Requirement | GuardDengue Implementation | Status |
| :--- | :--- | :--- | :---: |
| **1.1.1 Non-Text Content** | All images, icons, and emblems have meaningful text alternatives | All Lucide icons include `aria-hidden="true"` when decorative, or `aria-label` when interactive. Health shield emblem has `alt="GuardDengue Health Awareness Shield"`. | **PASS** |
| **1.4.1 Use of Color** | Color is never used as the sole medium for conveying meaning | Emergency alerts combine crimson `#B91C1C` with an `<AlertOctagon />` icon and explicit bold prefix: **"জরুরী সতর্কতা / Critical Advisory"**. | **PASS** |
| **1.4.3 Contrast (Minimum)** | Text contrast $\ge 4.5:1$ (Normal) and $\ge 3:1$ (Large) | Deep slate `#0F172A` on `#FDFBF7` canvas yields **17.27:1**. Action Amber `#B45309` with white text yields **5.02:1**. Emergency Crimson `#B91C1C` on `#FEF2F2` yields **5.91:1**. | **PASS** |
| **1.4.4 Resize Text** | Text scales cleanly up to $200\%$ without loss of content or breakage | Native GIGW text scaler (`A-` at 14px, `A` at 16px, `A+` at 18px) manipulates root `rem` scaling smoothly without horizontal layout scroll. | **PASS** |
| **1.4.12 Text Spacing** | Line height $\ge 1.5\times$ font size; paragraph spacing $\ge 2\times$ | Bengali typography (`Hind Siliguri`) applies `line-height: 1.75` scoped to prose reading blocks to prevent diacritic glyph overlap. | **PASS** |

### 2.2 Operable (Keyboard & Physical Access)

| Checklist Item | Requirement | GuardDengue Implementation | Status |
| :--- | :--- | :--- | :---: |
| **2.1.1 Keyboard Navigation** | All functions operable via Keyboard (`Tab`, `Enter`, `Space`, `Esc`) | Full keyboard tab index order. Modals, citation accordions, and the Inspector drawer can be opened and closed entirely via keyboard. | **PASS** |
| **2.1.2 No Keyboard Trap** | Focus is never trapped in a closed loop inside a component | Radix UI primitives handle focus trapping inside modals and release focus cleanly to the trigger button upon dismissal. | **PASS** |
| **2.4.1 Bypass Blocks** | Mechanism to skip repeated navigation blocks | First interactive element on every page is `<a href="#main-content" className="sr-only focus:not-sr-only">Skip to Main Content</a>`. | **PASS** |
| **2.4.7 Focus Visible** | Any keyboard operable element has a visible focus indicator | Explicit high-contrast focus rings on all interactive elements: `focus-visible:ring-2 focus-visible:ring-amber-700 focus-visible:outline-none`. | **PASS** |
| **2.5.5 Target Size** | Minimum touch target size $\ge 44 \times 44\text{px}$ | All buttons, quick prompts, language toggles, and send controls have minimum dimensions of $44\text{px}$. | **PASS** |

### 2.3 Understandable (Cognitive & Linguistic Access)

| Checklist Item | Requirement | GuardDengue Implementation | Status |
| :--- | :--- | :--- | :---: |
| **3.1.1 Language of Page** | Default human language of each web page can be programmatically determined | Root HTML sets `lang="en"` or `lang="bn"` dynamically via the `useLanguage` hook. | **PASS** |
| **3.1.2 Language of Parts** | Content rendered in a secondary language has explicit `lang` attribute | Bengali message bubbles inside an English session are tagged `<div lang="bn">...</div>` for accurate screen reader phonetics. | **PASS** |
| **3.3.1 Error Identification** | Errors are described in text with clear correction suggestions | Network disconnection or input errors display plain-language recovery steps in both English and Bengali, citing helpline `1800-313-444-222`. | **PASS** |

### 2.4 Robust (Assistive Technology Compatibility)

| Checklist Item | Requirement | GuardDengue Implementation | Status |
| :--- | :--- | :--- | :---: |
| **4.1.2 Name, Role, Value** | Controls have programmatic name, role, and states | Built on headless Radix UI / shadcn/ui components with full ARIA semantics (`aria-expanded`, `aria-controls`, `aria-haspopup`). | **PASS** |
| **4.1.3 Status Messages** | Live content updates announced to screen readers without acquiring focus | The chat output stream uses `<div role="status" aria-live="polite">` so new verified answers are spoken automatically by screen readers. | **PASS** |

---

## 3. High-Contrast Theme (GIGW Mandate)

When the citizen toggles **High Contrast Mode** from the GIGW top strip:
```css
[data-contrast="high"] {
  --color-wb-canvas: #000000 !important;
  --color-wb-surface: #121212 !important;
  --color-wb-border: #FFFF00 !important;
  --color-wb-text-main: #FFFFFF !important;
  --color-wb-text-muted: #FFFF00 !important;
  --color-wb-amber-700: #FFFF00 !important;
  --color-zone-emergency: #FF5555 !important;
  --color-zone-emergency-bg: #220000 !important;
  --color-zone-emergency-border: #FFFF00 !important;
  --color-zone-medication: #FFFF00 !important;
  --color-zone-medication-bg: #221100 !important;
  --color-zone-medication-border: #FFFF00 !important;
}

[data-contrast="high"] :focus-visible {
  outline: 3px solid #FFFF00 !important;
  outline-offset: 2px !important;
}
```
All borders and interactive focus rings turn high-contrast yellow (`#FFFF00`) over black (`#000000`), meeting strict government accessibility standards for low-vision citizens.

---

## 4. Motion & Reduced Motion Fallback

For citizens prone to vestibular motion sickness:
```css
@media (prefers-reduced-motion: reduce) {
  *, ::before, ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
All slide-overs and animated state transitions convert immediately to instant clean cuts when `prefers-reduced-motion` is detected.
