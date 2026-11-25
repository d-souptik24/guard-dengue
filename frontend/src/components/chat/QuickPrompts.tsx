/**
 * QuickPrompts — Civic Clinical Quick-Action Pills
 *
 * Provides citizens with one-tap access to critical dengue queries:
 * - Warning signs during defervescence
 * - Ibuprofen / Aspirin safety
 * - Severe stomach pain & vomiting
 * - Platelet thresholds
 *
 * Meets WCAG 2.1 AA 2.5.5 touch target size (min-h-[44px]).
 */
import { QUICK_PROMPTS } from '@/constants'
import { HelpCircle } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface QuickPromptsProps {
  onSelectPrompt: (promptText: string) => void
  disabled?: boolean
  className?: string
}

export default function QuickPrompts({
  onSelectPrompt,
  disabled = false,
  className = '',
}: QuickPromptsProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'
  const prompts = QUICK_PROMPTS[settings.language] || QUICK_PROMPTS.en

  return (
    <div className={`space-y-1.5 ${className}`}>
      <div className="flex items-center gap-1.5 text-[11px] font-semibold text-slate-600 px-1">
        <HelpCircle className="w-3.5 h-3.5 text-wb-amber-700 shrink-0" aria-hidden="true" />
        <span>{isBn ? 'সাধারণ ডেঙ্গু প্রশ্নসমূহ:' : 'Common Dengue Questions:'}</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {prompts.map((p, idx) => (
          <button
            key={idx}
            type="button"
            disabled={disabled}
            onClick={() => onSelectPrompt(p)}
            className="min-h-[44px] text-left px-3 py-2 rounded-xl text-xs bg-slate-50 hover:bg-amber-50/80 active:bg-amber-100/90 text-slate-800 hover:text-amber-950 border border-slate-200 hover:border-amber-300 transition-all cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed shadow-2xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-wb-amber-500 flex items-center"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  )
}
