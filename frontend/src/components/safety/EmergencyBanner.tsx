/**
 * EmergencyBanner — Zone 2 Deterministic Safety Red-Flag Alert
 *
 * Implements the core clinical mandate from WHO Dengue Guidelines (2024):
 * "Severe dengue frequently develops during defervescence (Days 3–7) when
 * fever subsides. Red flags require immediate hospital admission."
 */
import { useSettings } from '@/store/settings'
import { EMERGENCY_CONTACTS } from '@/constants'
import { AlertOctagon, PhoneCall, ArrowRight } from 'lucide-react'

interface EmergencyBannerProps {
  onSelectPrompt?: (prompt: string) => void
}

export default function EmergencyBanner({ onSelectPrompt }: EmergencyBannerProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <div
      role="alert"
      className="mb-6 rounded-2xl bg-gradient-to-r from-red-50 via-rose-50 to-orange-50 border-2 border-red-200 p-4 sm:p-5 shadow-sm text-slate-800"
    >
      <div className="flex flex-col sm:flex-row items-start gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-red-600 text-white flex items-center justify-center shrink-0 shadow-md shadow-red-600/20 mt-0.5">
          <AlertOctagon className="w-5 h-5 animate-pulse" />
        </div>

        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-sm sm:text-base font-bold text-red-950 tracking-tight">
              {isBn
                ? 'জরুরি সতর্কবার্তা: ডেঙ্গু ক্রিটিক্যাল ফেজ (জ্বর কমার সময়)'
                : 'Urgent Clinical Advisory: Critical Defervescence Phase'}
            </h2>
            <span className="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-red-100 text-red-800 rounded-full border border-red-300">
              {isBn ? 'জীবন বাঁচানোর নিয়ম' : 'Zero-Latency Rule'}
            </span>
          </div>

          <p className="text-xs sm:text-sm text-red-900 mt-1 leading-relaxed">
            {isBn ? (
              <>
                জ্বর কমার সময় (সাধারণত ৩য় থেকে ৭ম দিন) ডেঙ্গু রোগীর প্লাজমা লিকেজের ঝুঁকি বাড়ে।{' '}
                <strong>পেটে তীব্র ব্যথা, অনবরত বমি, মাড়ি বা নাক দিয়ে রক্তপাত, শ্বাসকষ্ট, অথবা অতিরিক্ত দুর্বলতা</strong>{' '}
                দেখা দিলে এক মুহূর্তও অপেক্ষা করবেন না।
              </>
            ) : (
              <>
                WHO guidelines emphasize that severe dengue complications often peak during defervescence (Days 3–7) as fever drops.{' '}
                <strong>Severe abdominal pain, persistent vomiting, mucosal bleeding, cold/clammy skin, or lethargy</strong>{' '}
                require immediate hospitalization.
              </>
            )}
          </p>

          <div className="mt-3 flex flex-wrap items-center gap-2.5">
            <a
              href={`tel:${EMERGENCY_CONTACTS.ambulance}`}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-red-700 text-white hover:bg-red-800 transition-colors shadow-xs cursor-pointer min-h-[36px]"
            >
              <PhoneCall className="w-3.5 h-3.5" />
              <span>{isBn ? 'অ্যাম্বুলেন্স কল করুন (১০৮)' : 'Dial Ambulance (108)'}</span>
            </a>

            <a
              href={`tel:${EMERGENCY_CONTACTS.stateHealth}`}
              className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-white text-red-700 border border-red-300 hover:bg-red-50 transition-colors shadow-xs cursor-pointer min-h-[36px]"
            >
              <span>{isBn ? 'রাজ্য স্বাস্থ্য কন্ট্রোল রুম:' : 'WB Health:'}</span>
              <strong className="font-mono">{EMERGENCY_CONTACTS.stateHealth}</strong>
            </a>

            {onSelectPrompt && (
              <button
                type="button"
                onClick={() =>
                  onSelectPrompt(
                    isBn
                      ? 'জ্বর কমলে কোন কোন লক্ষণ দেখলে হাসপাতালে যেতে হবে?'
                      : 'What symptoms in someone with possible dengue mean they should get urgent medical care?'
                  )
                }
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-red-900 hover:text-red-950 hover:bg-red-100/60 transition-colors cursor-pointer min-h-[36px]"
              >
                <span>{isBn ? 'সতর্কতা লক্ষণ বিস্তারিত জানুন' : 'Learn warning signs protocol'}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
