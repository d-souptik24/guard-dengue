/**
 * EmergencyRibbon — Zone 2 Critical Defervescence Advisory Banner
 *
 * Implements WHO 2024 Dengue Clinical Guidelines:
 * Warns citizens that when fever drops (Days 3-7), plasma leakage risk peaks.
 * Provides direct 108 ambulance dialer and interactive symptom prompt trigger.
 */
import { useSettings } from '@/store/settings'
import { EMERGENCY_CONTACTS } from '@/constants'
import { AlertOctagon, PhoneCall, ArrowRight } from 'lucide-react'

export interface EmergencyRibbonProps {
  onSelectPrompt?: (prompt: string) => void
  className?: string
}

export const EMERGENCY_RIBBON_PROMPT = {
  en: 'What emergency symptoms mean a dengue patient requires immediate hospital admission?',
  bn: 'ডেঙ্গু রোগীর কোন কোন উপসর্গ দেখা দিলে অবিলম্বে হাসপাতালে ভর্তি করা প্রয়োজন?',
} as const

export default function EmergencyRibbon({ onSelectPrompt, className = '' }: EmergencyRibbonProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  const promptText = isBn ? EMERGENCY_RIBBON_PROMPT.bn : EMERGENCY_RIBBON_PROMPT.en

  return (
    <aside
      role="alert"
      aria-labelledby="emergency-ribbon-heading"
      className={`rounded-xl bg-red-50 border-2 border-red-300 p-4 sm:p-5 text-red-950 shadow-xs transition-colors ${className}`}
    >
      <div className="flex flex-col sm:flex-row items-start gap-3.5">
        <div className="w-10 h-10 rounded-lg bg-zone-emergency text-white flex items-center justify-center shrink-0 shadow-xs mt-0.5">
          <AlertOctagon className="w-5 h-5 animate-pulse" aria-hidden="true" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <h2 id="emergency-ribbon-heading" className="text-sm sm:text-base font-bold text-red-950 tracking-tight">
              {isBn
                ? 'জরুরী সতর্কবার্তা: ডেঙ্গু ক্রিটিক্যাল ফেজ (জ্বর কমার সময় সতর্কতা)'
                : 'Critical Advisory: Defervescence Phase (When Fever Drops)'}
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-red-100 text-zone-emergency rounded-full border border-red-200">
              {isBn ? 'জীবন বাঁচানোর নিয়ম' : 'Days 3–7 Warning'}
            </span>
          </div>

          <p className="text-xs sm:text-sm text-red-900 mt-1 leading-relaxed">
            {isBn ? (
              <>
                জ্বর কমার সময় (সাধারণত ৩য় থেকে ৭ম দিন) ডেঙ্গু রোগীর প্লাজমা লিকেজের ঝুঁকি সর্বোচ্চ থাকে।{' '}
                <strong>পেটে তীব্র ব্যথা, অনবরত বমি, মাড়ি বা নাক দিয়ে রক্তপাত, শ্বাসকষ্ট, অথবা অতিরিক্ত দুর্বলতা</strong>{' '}
                দেখা দিলে অবিলম্বে হাসপাতালে যান।
              </>
            ) : (
              <>
                WHO guidelines emphasize that severe dengue complications peak during defervescence (Days 3–7) as fever drops.{' '}
                <strong>Severe abdominal pain, persistent vomiting, mucosal bleeding, difficulty breathing, or extreme lethargy</strong>{' '}
                require immediate hospital evaluation.
              </>
            )}
          </p>

          <div className="mt-3 flex flex-wrap items-center gap-2.5">
            <a
              href={`tel:${EMERGENCY_CONTACTS.ambulance}`}
              className="min-h-[44px] inline-flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold bg-zone-emergency text-white hover:bg-red-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-600 transition-colors shadow-xs"
            >
              <PhoneCall className="w-3.5 h-3.5" aria-hidden="true" />
              <span>{isBn ? 'অ্যাম্বুলেন্স কল করুন (১০৮)' : 'Dial Ambulance (108)'}</span>
            </a>

            {onSelectPrompt && (
              <button
                type="button"
                onClick={() => onSelectPrompt(promptText)}
                className="min-h-[44px] inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-red-900 bg-red-100/70 hover:bg-red-200/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-700 transition-colors cursor-pointer"
              >
                <span>{isBn ? 'জরুরি লক্ষণের সম্পূর্ণ তালিকা' : 'View hospital admission criteria'}</span>
                <ArrowRight className="w-3.5 h-3.5" aria-hidden="true" />
              </button>
            )}
          </div>
        </div>
      </div>
    </aside>
  )
}
