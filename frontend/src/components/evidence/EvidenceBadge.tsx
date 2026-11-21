/**
 * EvidenceBadge — Clinical Evidence Tier & Topic Badge
 *
 * Visualizes the 4-tier evidence level hierarchy:
 *   - Level 1: Global Clinical Practice Guideline (WHO)
 *   - Level 2: National Public Health Protocol (ICMR / NCVBDC)
 *   - Level 3: Public Health Operational Standard
 *   - Ungraded: Clinical Review
 */
import type { EvidenceLevel } from '@/types'
import { ShieldCheck, BookOpen, Award } from 'lucide-react'

export interface EvidenceBadgeProps {
  level: EvidenceLevel
  className?: string
}

export default function EvidenceBadge({ level, className = '' }: EvidenceBadgeProps) {
  const isLevel1 = level.startsWith('Level 1')
  const isLevel2 = level.startsWith('Level 2')

  let badgeColor = 'bg-slate-100 text-slate-800 border-slate-300'
  let Icon = BookOpen

  if (isLevel1) {
    badgeColor = 'bg-teal-50 text-teal-800 border-teal-300 ring-1 ring-teal-200'
    Icon = Award
  } else if (isLevel2) {
    badgeColor = 'bg-blue-50 text-blue-800 border-blue-300'
    Icon = ShieldCheck
  }

  return (
    <span
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${badgeColor} ${className}`}
    >
      <Icon className="w-3 h-3 shrink-0" aria-hidden="true" />
      <span>{level}</span>
    </span>
  )
}
