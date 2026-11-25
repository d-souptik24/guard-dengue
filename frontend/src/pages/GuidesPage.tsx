/**
 * GuidesPage — Dedicated Civic Clinical Action Guides & Triage Reference
 *
 * Provides a spacious, accessible overview of WHO and ICMR dengue protocols:
 * - Zone 2 Defervescence emergency advisory ribbon with direct 108 dialer
 * - Expanded 4-card action bento grid (Warning Signs, NSAID avoidance, Hydration, Testing)
 * - Clinical prompt forwarding: Selecting any topic navigates to the Sahayata Desk
 *   and automatically dispatches the inquiry to the live LangGraph stream.
 */
import { useNavigate } from 'react-router-dom'
import { useSettings } from '@/store/settings'
import EmergencyRibbon from '@/components/citizen/EmergencyRibbon'
import CitizenBentoGrid from '@/components/citizen/CitizenBentoGrid'
import { BookOpen, ShieldCheck } from 'lucide-react'

export default function GuidesPage() {
  const navigate = useNavigate()
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  const handleSelectPrompt = (prompt: string) => {
    navigate('/', { state: { initialPrompt: prompt } })
  }

  return (
    <div className="w-full max-w-5xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header Introduction */}
      <section className="bg-white rounded-2xl border border-wb-border p-6 sm:p-8 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-teal-50 text-teal-800 border border-teal-200">
              <BookOpen className="w-4 h-4 text-teal-700" aria-hidden="true" />
              <span>{isBn ? 'ক্লিনিক্যাল নির্দেশিকা সংগ্রহ' : 'Clinical Protocol Repository'}</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              {isBn ? 'নাগরিক স্বাস্থ্য ও প্রতিরোধ নির্দেশিকা' : 'Citizen Health & Clinical Guides'}
            </h1>
            <p className="text-xs sm:text-sm text-slate-600 max-w-2xl leading-relaxed">
              {isBn
                ? 'পশ্চিমবঙ্গ স্বাস্থ্য দপ্তর, বিশ্ব স্বাস্থ্য সংস্থা (WHO 2024) এবং আইসিএমআর (ICMR) নির্দেশিকা অনুযায়ী জরুরি বিপৎচিহ্ন, তরল গ্রহণ ও ওষুধ সুরক্ষার প্রামাণ্য তথ্য।'
                : 'Evidence-grounded health protocols for warning sign identification, fluid intake, NSAID contraindication, and diagnostic timing aligned with WHO 2024 and ICMR.'}
            </p>
          </div>

          <div className="hidden sm:flex flex-col items-end shrink-0 text-right">
            <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-800 bg-teal-50/80 px-3 py-1.5 rounded-lg border border-teal-200/80">
              <ShieldCheck className="w-4 h-4 text-teal-600" aria-hidden="true" />
              <span>GRADE Level 1 Evidence</span>
            </span>
            <span className="text-[10px] text-slate-400 font-mono mt-1">
              Corpus: 2026.09-v2-approved
            </span>
          </div>
        </div>
      </section>

      {/* Critical Defervescence Alert Ribbon */}
      <EmergencyRibbon onSelectPrompt={handleSelectPrompt} />

      {/* Action Bento Grid */}
      <section aria-labelledby="guides-grid-heading" className="space-y-4">
        <div className="flex items-center justify-between px-1">
          <h2 id="guides-grid-heading" className="text-sm font-bold uppercase tracking-wider text-slate-700">
            {isBn ? 'প্রামাণ্য স্বাস্থ্য বিষয়সমূহ' : 'Evidence-Grounded Reference Guides'}
          </h2>
          <span className="text-xs text-slate-500">
            {isBn ? 'সহায়তা ডেস্কে উত্তর পেতে কার্ডে ক্লিক করুন' : 'Click any guide to ask Sahayata Desk'}
          </span>
        </div>

        <CitizenBentoGrid onSelectPrompt={handleSelectPrompt} />
      </section>
    </div>
  )
}
