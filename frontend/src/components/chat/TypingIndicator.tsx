/**
 * TypingIndicator — Staged Clinical Verification Pulse
 *
 * Visualizes the 2-stage verification workflow:
 *   Stage 1: Symptom Screening & Guideline Retrieval
 *   Stage 2: NLI Grounding Verification Gate (WHO/ICMR Rules)
 *
 * Uses role="status" and aria-live="polite" for screen reader accessibility.
 */
import { Activity, ShieldCheck } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface TypingIndicatorProps {
  stage?: 'screening' | 'verifying'
  className?: string
}

export default function TypingIndicator({
  stage = 'verifying',
  className = '',
}: TypingIndicatorProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  const label =
    stage === 'screening'
      ? isBn
        ? 'লক্ষণ ও নির্দেশিকা অনুসন্ধান করা হচ্ছে...'
        : 'Screening symptoms & searching guidelines...'
      : isBn
        ? 'ক্লিনিক্যাল সুরক্ষা ও তথ্য যাচাই করা হচ্ছে...'
        : 'Verifying clinical safety & evidence rules...'

  return (
    <div
      role="status"
      aria-live="polite"
      className={`inline-flex items-center gap-2.5 px-4 py-2.5 rounded-2xl bg-white border border-slate-200/90 shadow-xs text-xs text-slate-700 animate-in fade-in duration-200 ${className}`}
    >
      {stage === 'screening' ? (
        <Activity className="w-4 h-4 text-wb-amber-700 animate-pulse shrink-0" aria-hidden="true" />
      ) : (
        <ShieldCheck className="w-4 h-4 text-wb-teal-evidence animate-pulse shrink-0" aria-hidden="true" />
      )}

      <span className="font-medium text-slate-800">{label}</span>

      <span className="flex items-center gap-1 pl-1">
        <span className="w-1.5 h-1.5 rounded-full bg-wb-amber-600 animate-bounce [animation-delay:-0.3s]" />
        <span className="w-1.5 h-1.5 rounded-full bg-wb-amber-600 animate-bounce [animation-delay:-0.15s]" />
        <span className="w-1.5 h-1.5 rounded-full bg-wb-amber-600 animate-bounce" />
      </span>
    </div>
  )
}
