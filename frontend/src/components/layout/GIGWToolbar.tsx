/**
 * GIGWToolbar — Top Government Accessibility Strip (GIGW 3.0 & WCAG 2.1 AA)
 *
 * Implements:
 * - Keyboard "Skip to main content" (with tabIndex={-1} programmatic focus)
 * - Text scaling: A- (14px), A (16px), A+ (18px)
 * - High Contrast Mode toggle ([data-contrast="high"])
 * - Bilingual parity switcher (English / বাংলা)
 */
import { useSettings } from '@/store/settings'
import type { FontSize } from '@/types'
import { Eye, Languages } from 'lucide-react'

export interface GIGWToolbarProps {
  className?: string
}

export default function GIGWToolbar({ className = '' }: GIGWToolbarProps) {
  const { settings, setLanguage, setFontSize, setContrast } = useSettings()
  const isBn = settings.language === 'bn'
  const isHighContrast = settings.contrast === 'high'

  const fontSizes: { size: FontSize; label: string; ariaLabel: string }[] = [
    { size: 'sm', label: 'A-', ariaLabel: isBn ? 'ছোট ফন্ট' : 'Small font (14px)' },
    { size: 'md', label: 'A',  ariaLabel: isBn ? 'স্বাভাবিক ফন্ট' : 'Default font (16px)' },
    { size: 'lg', label: 'A+', ariaLabel: isBn ? 'বড় ফন্ট' : 'Large font (18px)' },
  ]

  return (
    <div
      role="region"
      aria-label={isBn ? 'অভিগম্যতা নিয়ন্ত্রণ বার' : 'Accessibility controls'}
      className={`w-full bg-wb-canvas text-wb-text-main border-b border-wb-border text-xs py-1 px-4 sm:px-6 select-none ${className}`}
    >
      {/* Keyboard Skip to Main Content Link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:top-2 focus:left-4 focus:px-3 focus:py-2 focus:bg-wb-amber-700 focus:text-white focus:rounded-md focus:shadow-md focus:outline-none focus:ring-2 focus:ring-wb-amber-500 min-h-[44px] flex items-center font-semibold"
      >
        {isBn ? 'মূল বিষয়বস্তুতে যান' : 'Skip to main content'}
      </a>

      <div className="w-full max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        {/* Government Affiliation Label */}
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0" aria-hidden="true" />
          <span className="font-medium text-[11px] sm:text-xs text-wb-text-main">
            <span className="hidden sm:inline">
              {isBn
                ? 'পশ্চিমবঙ্গ সরকার • স্বাস্থ্য ও পরিবার কল্যাণ দপ্তর'
                : 'Government of West Bengal • Department of Health & Family Welfare'}
            </span>
            <span className="sm:hidden">
              {isBn ? 'পশ্চিমবঙ্গ স্বাস্থ্য দপ্তর' : 'Govt of West Bengal • Health'}
            </span>
          </span>
        </div>

        {/* Accessibility & Language Controls */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Font Size Scaler */}
          <div
            role="group"
            aria-label={isBn ? 'ফন্ট সাইজ পরিবর্তন' : 'Font size scaling'}
            className="flex items-center bg-wb-surface border border-wb-border rounded-md p-0.5"
          >
            {fontSizes.map(({ size, label, ariaLabel }) => {
              const isActive = settings.fontSize === size
              return (
                <button
                  key={size}
                  type="button"
                  onClick={() => setFontSize(size)}
                  aria-pressed={isActive}
                  aria-label={ariaLabel}
                  className={`min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2 py-1 text-xs rounded transition-all cursor-pointer font-semibold ${
                    isActive
                      ? 'bg-wb-amber-700 text-white shadow-xs'
                      : 'text-wb-text-muted hover:text-wb-text-main'
                  }`}
                >
                  {label}
                </button>
              )
            })}
          </div>

          {/* High Contrast Toggle */}
          <button
            type="button"
            onClick={() => setContrast(isHighContrast ? 'normal' : 'high')}
            aria-pressed={isHighContrast}
            aria-label={isBn ? 'উচ্চ বৈসাদৃশ্য মোড' : 'Toggle High Contrast Mode'}
            className={`min-h-[44px] inline-flex items-center gap-1.5 px-3 py-1 text-xs font-semibold rounded-md border transition-all cursor-pointer ${
              isHighContrast
                ? 'bg-black text-yellow-300 border-yellow-300 ring-2 ring-yellow-300'
                : 'bg-wb-surface text-wb-text-main border-wb-border hover:bg-slate-50'
            }`}
          >
            <Eye className="w-4 h-4" aria-hidden="true" />
            <span className="hidden sm:inline">
              {isHighContrast ? (isBn ? 'উচ্চ বৈসাদৃশ্য' : 'High Contrast') : (isBn ? 'বৈসাদৃশ্য' : 'Contrast')}
            </span>
          </button>

          {/* Bilingual Switcher */}
          <div
            role="group"
            aria-label={isBn ? 'ভাষা নির্বাচন' : 'Language selector'}
            className="flex items-center bg-wb-surface border border-wb-border rounded-md p-0.5"
          >
            <span className="px-1 text-wb-text-muted" aria-hidden="true">
              <Languages className="w-4 h-4" />
            </span>
            <button
              type="button"
              onClick={() => setLanguage('en')}
              aria-pressed={!isBn}
              className={`min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 text-xs rounded transition-all cursor-pointer font-semibold ${
                !isBn
                  ? 'bg-wb-amber-700 text-white shadow-xs'
                  : 'text-wb-text-muted hover:text-wb-text-main'
              }`}
            >
              EN
            </button>
            <button
              type="button"
              onClick={() => setLanguage('bn')}
              aria-pressed={isBn}
              className={`min-h-[44px] min-w-[44px] inline-flex items-center justify-center px-2.5 py-1 text-xs rounded transition-all cursor-pointer font-semibold ${
                isBn
                  ? 'bg-wb-amber-700 text-white shadow-xs'
                  : 'text-wb-text-muted hover:text-wb-text-main'
              }`}
            >
              বাংলা
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
