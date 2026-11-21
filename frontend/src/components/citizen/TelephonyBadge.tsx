/**
 * TelephonyBadge — West Bengal Emergency Telephony Hub
 *
 * Provides direct one-tap dialing to:
 * - 108 / 102 (Ambulance Service)
 * - 1800-313-444-222 (Swasthya Bhawan State Health Helpline)
 *
 * Conforms to WCAG 2.1 AA with touch targets >= 44px.
 */
import { useSettings } from '@/store/settings'
import { EMERGENCY_CONTACTS } from '@/constants'
import { PhoneCall, Ambulance } from 'lucide-react'

export interface TelephonyBadgeProps {
  className?: string
}

export default function TelephonyBadge({ className = '' }: TelephonyBadgeProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  // Clean numbers for tel: protocol without hyphens
  const ambulanceTel = `tel:${EMERGENCY_CONTACTS.ambulance}`
  const stateHealthTel = `tel:${EMERGENCY_CONTACTS.stateHealth.replace(/-/g, '')}`

  return (
    <div
      role="region"
      aria-label={isBn ? 'জরুরি হেল্পলাইন নম্বর' : 'Emergency helplines'}
      className={`flex flex-wrap items-center gap-2 ${className}`}
    >
      {/* 108 Ambulance Button */}
      <a
        href={ambulanceTel}
        className="min-h-[44px] inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold bg-white text-wb-ochre-900 border border-amber-200 hover:bg-amber-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white transition-all shadow-xs shrink-0"
        title={isBn ? 'অ্যাম্বুলেন্স কল করুন (১০৮ / ১০২)' : 'Call Ambulance (108 / 102)'}
      >
        <span className="p-1 rounded-md bg-zone-emergency text-white shrink-0">
          <Ambulance className="w-3.5 h-3.5" aria-hidden="true" />
        </span>
        <span className="leading-tight">
          <span className="block text-[10px] font-medium text-slate-500 uppercase">
            {isBn ? 'অ্যাম্বুলেন্স' : 'Ambulance'}
          </span>
          <span className="font-mono text-xs font-extrabold text-zone-emergency">108 / 102</span>
        </span>
      </a>

      {/* Swasthya Bhawan Helpline */}
      <a
        href={stateHealthTel}
        className="min-h-[44px] hidden sm:inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold bg-wb-ochre-900/60 text-white border border-amber-400/30 hover:bg-wb-ochre-900/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white transition-all shadow-xs shrink-0"
        title={isBn ? 'স্বাস্থ্য ভবন হেল্পলাইন (১৮০০-৩১৩-৪৪৪-২২২)' : 'Swasthya Bhawan Helpline (1800-313-444-222)'}
      >
        <PhoneCall className="w-3.5 h-3.5 text-amber-300 shrink-0" aria-hidden="true" />
        <span className="leading-tight">
          <span className="block text-[10px] font-normal text-amber-200">
            {isBn ? 'স্বাস্থ্য ভবন হেল্পলাইন' : 'State Helpline'}
          </span>
          <span className="font-mono text-xs font-bold text-white">1800-313-444-222</span>
        </span>
      </a>
    </div>
  )
}
