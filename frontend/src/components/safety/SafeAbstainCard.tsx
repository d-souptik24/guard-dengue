/**
 * SafeAbstainCard — Out-of-Scope & Safe Abstention Notice (Zone 2)
 *
 * Renders when:
 * 1. A user query lacks sufficient grounded clinical evidence in WHO/ICMR corpora.
 * 2. A query asks for personalized clinical diagnosis or prescription beyond public health education.
 *
 * Directs citizens to registered clinicians and the WB State Health Helpline (1800-313-444-222).
 */
import { Info, PhoneCall } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface SafeAbstainCardProps {
  reason?: string
  className?: string
}

export default function SafeAbstainCard({ reason, className = '' }: SafeAbstainCardProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <div
      role="region"
      aria-label={isBn ? 'সতর্কতামূলক নির্দেশনা' : 'Educational Abstention Advisory'}
      className={`w-full rounded-xl bg-slate-50 border border-slate-300/80 p-4 sm:p-5 shadow-xs ${className}`}
    >
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-lg bg-slate-200/80 text-slate-700 flex items-center justify-center shrink-0">
          <Info className="w-5 h-5" aria-hidden="true" />
        </div>

        <div className="space-y-2 flex-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h3 className="text-xs sm:text-sm font-bold text-slate-900 leading-tight">
              {isBn ? 'অনুমোদিত তথ্যের সীমাবদ্ধতা' : 'Health Education Scope Limit'}
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-200 text-slate-700">
              {isBn ? 'নিরাপদ নিরবতা (Safe Abstention)' : 'Uncertain / Abstain'}
            </span>
          </div>

          <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
            {isBn
              ? 'একটি দায়িত্বশীল স্বাস্থ্য সচেতনতা ব্যবস্থা হিসেবে, পর্যাপ্ত অনুমোদিত ক্লিনিক্যাল প্রমাণের অভাবে আমি এই প্রশ্নের নিশ্চিত উত্তর দিতে পারছি না। ডেঙ্গুর যে কোনো নির্দিষ্ট চিকিৎসা বা রোগ নির্ণয়ের জন্য সরাসরি চিকিৎসকের পরামর্শ নেওয়া বাধ্যতামূলক।'
              : 'As an evidence-grounded health education tool, GuardDengue abstains from generating unverified answers without direct clinical guideline support. For personalized medical diagnosis or therapy, please consult a registered physician.'}
          </p>

          {reason && (
            <div className="text-[11px] text-slate-600 bg-white/70 rounded p-2 border border-slate-200">
              <strong>{isBn ? 'কারিগরি কারণ: ' : 'Auditor Note: '}</strong>
              {reason}
            </div>
          )}

          <div className="pt-2 flex flex-wrap items-center gap-2">
            <a
              href="tel:1800313444222"
              className="min-h-[44px] px-3.5 py-1.5 rounded-lg bg-wb-blue-700 hover:bg-wb-blue-800 text-white font-semibold text-xs flex items-center gap-1.5 transition-colors cursor-pointer shadow-xs"
            >
              <PhoneCall className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{isBn ? '১৮০০-৩১৩-৪৪৪-২২২ হেল্পলাইনে কল করুন' : 'Call 1800-313-444-222 Helpline'}</span>
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
