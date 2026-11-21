# GuardDengue: Style Guide & Tailwind CSS v4 Design Tokens

> **Document Type:** Machine-Readable & Human-Readable Design Token System  
> **Framework:** Tailwind CSS v4 (CSS-first `@theme` Architecture)  
> **Compliance:** WCAG 2.1 Level AA (4.5:1+ contrast) & UX4G 2.0  
> **Status:** REVISED TOKEN SPECIFICATION (PENDING FINAL REVIEW)  

---

## 1. Overview & Token Architecture

Tailwind CSS v4 replaces legacy JavaScript configuration files with pure CSS custom property declarations within `@theme`. All GuardDengue components bind strictly to these semantic tokens, eliminating arbitrary hex values and uncontrolled spacing.

---

## 2. Color Tokens (CSS Custom Properties)

```css
@theme {
  /* =========================================================================
     1. Official West Bengal Civic Palette (Amber, Ochre & Saffron)
     ========================================================================= */
  --color-wb-amber-50: #FFFBEB;
  --color-wb-amber-100: #FEF3C7;
  --color-wb-amber-200: #FDE68A;
  --color-wb-amber-500: #F59E0B; /* Golden Saffron Highlight (Dark-text only) */
  --color-wb-amber-600: #D97706; /* Civic Accent Border */
  --color-wb-amber-700: #B45309; /* Primary Action Amber (White-text safe: 5.02:1) */

  --color-wb-ochre-800: #92400E; /* Bengal Heritage Ochre (White-text safe: 7.09:1) */
  --color-wb-ochre-900: #78350F; /* Deep Administrative Tone */

  /* =========================================================================
     2. Civic Utility & Lifeline Telephony
     ========================================================================= */
  --color-wb-blue-700: #1D4ED8;
  --color-wb-blue-800: #1E3A8A; /* Swasthya Helpline & 108 Tile (10.36:1) */
  --color-wb-blue-900: #0F172A;

  /* =========================================================================
     3. Clinical Safety Semantic Zones (GuardDengue 5-Zone Model)
     ========================================================================= */
  --color-zone-emergency: #B91C1C;        /* Zone 2: Critical Defervescence Warning (5.91:1) */
  --color-zone-emergency-bg: #FEF2F2;
  --color-zone-emergency-border: #F87171;

  --color-zone-medication: #B45309;       /* Zone 2: NSAID Avoidance Interceptor (4.84:1) */
  --color-zone-medication-bg: #FFFBEB;
  --color-zone-medication-border: #FCD34D;

  --color-zone-verified: #0F766E;         /* Zone 5: Verified Evidence-Grounded Response (5.25:1) */
  --color-zone-verified-bg: #F0FDFA;
  --color-zone-verified-border: #99F6E4;

  --color-zone-uncertain: #64748B;        /* Safe Abstention Pathway */
  --color-zone-uncertain-bg: #F8FAFC;
  --color-zone-uncertain-border: #CBD5E1;

  /* =========================================================================
     4. Canvas & Typography Neutrals
     ========================================================================= */
  --color-wb-canvas: #FDFBF7;             /* Warm Civic Linen (Page Background) */
  --color-wb-surface: #FFFFFF;            /* Pure Card Surface */
  --color-wb-border: #E2E8F0;             /* Standard Civic Border */
  --color-wb-text-main: #0F172A;          /* Deep Slate Ink (17.27:1 on Linen) */
  --color-wb-text-muted: #475569;         /* Secondary Administrative Text (7.33:1) */

  /* =========================================================================
     5. Typography Stacks (Tailwind v4 syntax: generates font-english & font-bengali)
     ========================================================================= */
  --font-english: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-bengali: "Hind Siliguri", "Noto Sans Bengali", sans-serif;
}
```

---

## 3. Typography Rules & Scoped Bengali Leading

To ensure authentic multilingual rendering without breaking compact buttons or badges:

```css
/* Default body font using Inter */
body {
  font-family: var(--font-english);
  background-color: var(--color-wb-canvas);
  color: var(--color-wb-text-main);
  -webkit-font-smoothing: antialiased;
}

/* Scoped Bengali font family */
:lang(bn) {
  font-family: var(--font-bengali);
}

/* Vertical line-height clearance applied strictly to prose reading blocks */
:lang(bn) p,
:lang(bn) .prose-bengali,
:lang(bn) .chat-message-content {
  line-height: 1.75;
  letter-spacing: 0.01em;
}
```

---

## 4. GIGW Accessibility & Text Scaling Tokens

Root font-size scaling values for user-controlled accessibility adjustments:

| Token Name | Value | Purpose |
| :--- | :--- | :--- |
| `--text-scale-small` | `14px` | GIGW `A-` Font Scaler |
| `--text-scale-default` | `16px` | GIGW `A` Default Font Scaler |
| `--text-scale-large` | `18px` | GIGW `A+` Font Scaler |

### High-Contrast Theme Override Block (`[data-contrast="high"]`):
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

---

## 5. Spacing, Sizing & Control Heights

GuardDengue enforces an **$8\text{px}$ Base Spacing Grid** with strict touch-target minimums:

| Dimension | Token Value | Purpose |
| :--- | :--- | :--- |
| **Minimum Touch Target** | `44px` (`min-h-[44px] min-w-[44px]`) | WCAG AA compliance for mobile buttons and controls |
| **Input Bar Height** | `52px` (`h-[52px]`) | Comfortable citizen typing target |
| **Masthead Height** | `88px` (Desktop) / `64px` (Mobile) | Official governmental presence |
| **Accessibility Strip** | `34px` | Compact GIGW utility bar |
| **Card Padding** | `24px` (`p-6`) on desktop, `16px` (`p-4`) on mobile | Balanced negative space |

---

## 6. Two-Tier Border Radius Scale

To ensure clean visual consistency without awkward bulging corners:
- **Container Radius:** `rounded-xl` ($12\text{px}$) for cards, modal dialogs, and citizen bento tiles.
- **Control Radius:** `rounded-lg` ($8\text{px}$) for buttons, textareas, inputs, and dropdown items.
- **Status Chips:** `rounded-full` reserved strictly for compact metadata chips (`Level 1 Evidence`, `Ambulance 108`).

---

## 7. Contrast Compliance Matrix (Verified WCAG 2.1 AA Ratios)

The table below documents the exact calculated contrast ratios against WCAG 2.1 standards:

| Foreground Color | Background Color | Calculated Contrast | Pass / Fail |
| :--- | :--- | :--- | :---: |
| **Deep Slate Ink (`#0F172A`)** | Warm Civic Linen (`#FDFBF7`) | **17.27 : 1** | **PASS (AAA)** |
| **Deep Slate Ink (`#0F172A`)** | Pure White (`#FFFFFF`) | **17.85 : 1** | **PASS (AAA)** |
| **White (`#FFFFFF`)** | Action Amber (`#B45309`) | **5.02 : 1** | **PASS (AA)** |
| **White (`#FFFFFF`)** | Heritage Ochre (`#92400E`) | **7.09 : 1** | **PASS (AAA)** |
| **White (`#FFFFFF`)** | Telephony Blue (`#1E3A8A`) | **10.36 : 1** | **PASS (AAA)** |
| **Emergency Crimson (`#B91C1C`)**| Emergency Linen (`#FEF2F2`) | **5.91 : 1** | **PASS (AA)** |
| **Medication Amber (`#B45309`)** | Medication Linen (`#FFFBEB`) | **4.84 : 1** | **PASS (AA)** |
| **Evidence Teal (`#0F766E`)** | Evidence Linen (`#F0FDFA`) | **5.25 : 1** | **PASS (AA)** |
| **Slate Muted (`#475569`)** | Warm Civic Linen (`#FDFBF7`) | **7.33 : 1** | **PASS (AAA)** |

*(Note: White text on `#D97706` [$3.19:1$] and `#F59E0B` [$2.15:1$] fails WCAG AA and is strictly prohibited).*
