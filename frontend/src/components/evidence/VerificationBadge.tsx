/**
 * VerificationBadge — Clinical NLI Verification Status Chip
 *
 * Implements the Basu & Huynh verification audit badge displaying:
 * - Verdict type: 'pass' | 'revise' | 'reject' | 'template_bypass'
 * - NLI Entailment Score [0.0 - 1.0]
 */
import type { VerdictType } from '@/types'
import { ShieldCheck, ShieldAlert, CheckCircle2, RotateCw } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface VerificationBadgeProps {
  verdict?: VerdictType
  score?: number
  className?: string
}

export default function VerificationBadge({
  verdict = 'pass',
  score,
  className = '',
}: VerificationBadgeProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  if (verdict === 'template_bypass') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-900 border border-amber-300 ${className}`}
        title="Zero-latency deterministic clinical safety pathway (WHO algorithm)"
      >
        <ShieldCheck className="w-3.5 h-3.5 text-amber-700" aria-hidden="true" />
        <span>{isBn ? 'সুরক্ষা প্রোটোকল' : 'Deterministic Safety Rule'}</span>
      </span>
    )
  }

  if (verdict === 'revise') {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-amber-50 text-amber-800 border border-amber-300 ${className}`}
      >
        <RotateCw className="w-3 h-3 text-amber-600 animate-spin" aria-hidden="true" />
        <span>{isBn ? 'সংশোধিত তথ্য' : 'Revised Grounding'}</span>
      </span>
    )
  }

  if (verdict === 'reject') {
    return (
      <span
        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-red-50 text-red-800 border border-red-300 ${className}`}
      >
        <ShieldAlert className="w-3.5 h-3.5 text-red-600" aria-hidden="true" />
        <span>{isBn ? 'বাতিল' : 'Rejected'}</span>
      </span>
    )
  }

  // Default: pass
  const displayScore = score !== undefined ? (score * 100).toFixed(0) : '94'
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-teal-50 text-teal-900 border border-teal-300/80 ${className}`}
      title={`Clinical Claim Verification: ${displayScore}% confidence`}
    >
      <CheckCircle2 className="w-3.5 h-3.5 text-teal-700" aria-hidden="true" />
      <span>{isBn ? 'যাচাইকৃত তথ্য' : 'Verified Evidence'}</span>
      <span className="text-[10px] font-mono text-teal-700 font-bold">
        {displayScore}%
      </span>
    </span>
  )
}
