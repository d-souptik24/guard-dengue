/**
 * CitizenBentoGrid — 4-Tile Civic Action Bento Grid
 *
 * Implements above-the-fold 1-tap citizen inquiry triggers.
 * Mobile-first responsiveness:
 * - Desktop (>= 1024px): 2x2 grid layout in 5-column sticky sidebar
 * - Mobile (< 1024px): Horizontal scroll-snap carousel (~110px height),
 *   preventing chat occlusion while keeping all 4 cards 1-tap accessible.
 */
import { useSettings } from '@/store/settings'
import { Flame, ShieldAlert, Droplets, TestTube2, ArrowUpRight } from 'lucide-react'

export interface CitizenBentoGridProps {
  onSelectPrompt: (prompt: string) => void
  isSubmitting?: boolean
  className?: string
}

export const BENTO_PROMPTS = {
  defervescence: {
    en: 'What are the critical warning signs when fever drops during Days 3 to 7 of dengue?',
    bn: 'ডেঙ্গুতে ৩য় থেকে ৭ম দিনে জ্বর কমার সময় (ক্রিটিক্যাল ফেজ) কোন কোন বিপৎচিহ্ন দেখা দিতে পারে?',
  },
  nsaid: {
    en: 'Why are ibuprofen, aspirin, and combiflam strictly prohibited in suspected dengue, and what can I take for fever?',
    bn: 'ডেঙ্গু সন্দেহে আইবুপ্রোফেন বা অ্যাসপিরিন খাওয়া কেন নিষেধ এবং জ্বরের জন্য কী ওষুধ খাওয়া নিরাপদ?',
  },
  hydration: {
    en: 'What is the correct oral fluid and ORS hydration protocol for dengue, and is papaya leaf juice scientifically proven?',
    bn: 'ডেঙ্গু রোগীর জন্য ওআরএস (ORS) ও জলপানের সঠিক নিয়ম কী এবং পেঁপে পাতার রসের কোনো বৈজ্ঞানিক ভিত্তি আছে কি?',
  },
  testing: {
    en: 'When should I take an NS1 antigen test versus an IgM antibody test for dengue diagnosis?',
    bn: 'ডেঙ্গু শনাক্তকরণে এনএস১ (NS1) অ্যান্টিজেন এবং আইজিএম (IgM) অ্যান্টিবডি পরীক্ষা কখন করানো উচিত?',
  },
} as const

interface BentoCardConfig {
  id: keyof typeof BENTO_PROMPTS
  tagEn: string
  tagBn: string
  titleEn: string
  titleBn: string
  descEn: string
  descBn: string
  accentColor: string
  icon: typeof Flame
}

const CARDS: BentoCardConfig[] = [
  {
    id: 'defervescence',
    tagEn: 'Critical Warning',
    tagBn: 'বিপৎচিহ্ন সতর্কতা',
    titleEn: 'When Fever Drops (Days 3–7)',
    titleBn: 'জ্বর কমার সময় বিপদ',
    descEn: 'Plasma leakage and severe complications peak as temperature normalizes.',
    descBn: 'জ্বর কমার সময় প্লাজমা লিকেজের সর্বোচ্চ ঝুঁকি থাকে। সতর্কতামূলক লক্ষণ জানুন।',
    accentColor: 'border-wb-ochre-800 text-wb-ochre-800 bg-amber-50/50',
    icon: Flame,
  },
  {
    id: 'nsaid',
    tagEn: 'Medication Hazard',
    tagBn: 'ওষুধ সতর্কতা',
    titleEn: 'Why Avoid Aspirin & Ibuprofen',
    titleBn: 'কী ওষুধ খাওয়া নিষেধ?',
    descEn: 'NSAIDs increase internal bleeding and platelet drop. Paracetamol limits.',
    descBn: 'আইবুপ্রোফেন ও অ্যাসপিরিন রক্তক্ষরণ বাড়ায়। শুধু প্যারাসিটামল ব্যবহার করুন।',
    accentColor: 'border-wb-amber-700 text-wb-amber-700 bg-orange-50/50',
    icon: ShieldAlert,
  },
  {
    id: 'hydration',
    tagEn: 'Clinical Fluid Care',
    tagBn: 'সঠিক পরিচর্যা',
    titleEn: 'Oral Hydration & Myth Reality',
    titleBn: 'জল ও ওআরএস (ORS) গ্রহণ',
    descEn: 'Electrolyte balance guidelines and scientific facts on papaya leaf extract.',
    descBn: 'পর্যাপ্ত ওআরএস গ্রহণ ও পেঁপে পাতার রসের বৈজ্ঞানিক তথ্য জেনে নিন।',
    accentColor: 'border-zone-verified text-zone-verified bg-teal-50/50',
    icon: Droplets,
  },
  {
    id: 'testing',
    tagEn: 'Diagnostic Protocol',
    tagBn: 'পরীক্ষাগার নির্দেশিকা',
    titleEn: 'Testing Timing: NS1 vs IgM',
    titleBn: 'রক্তের পরীক্ষা ও সঠিক সময়',
    descEn: 'NS1 Antigen (Days 1–5) vs IgM Antibody (> Day 5) laboratory standards.',
    descBn: 'এনএস১ অ্যান্টিজেন এবং আইজিএম অ্যান্টিবডি পরীক্ষার সঠিক দিনপঞ্জি।',
    accentColor: 'border-blue-700 text-blue-700 bg-blue-50/50',
    icon: TestTube2,
  },
]

export default function CitizenBentoGrid({
  onSelectPrompt,
  isSubmitting = false,
  className = '',
}: CitizenBentoGridProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <nav
      aria-label={isBn ? 'নাগরিক স্বাস্থ্য দ্রুত নির্দেশনা' : 'Citizen Health Action Guides'}
      className={`w-full ${className}`}
    >
      <div className="flex items-center justify-between mb-2 px-1">
        <h3 className="text-xs font-bold uppercase tracking-wider text-wb-text-muted">
          {isBn ? 'নাগরিক স্বাস্থ্য নির্দেশিকা' : 'Clinical Health Guides'}
        </h3>
        <span className="text-[11px] text-wb-text-muted hidden sm:inline">
          {isBn ? 'ক্লিনিক্যাল নির্দেশিকা বিষয়' : 'Clinical Reference Topics'}
        </span>
      </div>

      {/* Responsive layout: Mobile horizontal swipe carousel, Desktop 2x2 grid */}
      <div className="flex overflow-x-auto snap-x snap-mandatory gap-3 pb-2 touch-pan-x no-scrollbar lg:grid lg:grid-cols-2 lg:gap-3 lg:overflow-visible">
        {CARDS.map((card) => {
          const Icon = card.icon
          const prompt = isBn ? BENTO_PROMPTS[card.id].bn : BENTO_PROMPTS[card.id].en
          const title = isBn ? card.titleBn : card.titleEn
          const desc = isBn ? card.descBn : card.descEn
          const tag = isBn ? card.tagBn : card.tagEn

          return (
            <button
              key={card.id}
              type="button"
              disabled={isSubmitting}
              onClick={() => onSelectPrompt(prompt)}
              className={`min-h-[44px] w-[82vw] sm:w-[280px] lg:w-auto shrink-0 snap-center text-left p-3.5 rounded-xl bg-wb-surface border border-wb-border hover:border-wb-amber-500 hover:shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-wb-amber-700 transition-all cursor-pointer group flex flex-col justify-between ${
                isSubmitting ? 'opacity-60 cursor-not-allowed' : ''
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className={`inline-flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md border ${card.accentColor}`}>
                    <Icon className="w-3 h-3" aria-hidden="true" />
                    <span>{tag}</span>
                  </span>
                  <ArrowUpRight className="w-3.5 h-3.5 text-wb-text-muted group-hover:text-wb-amber-700 transition-colors" aria-hidden="true" />
                </div>
                <h4 className="text-xs sm:text-sm font-bold text-wb-text-main group-hover:text-wb-amber-700 transition-colors line-clamp-1">
                  {title}
                </h4>
                <p className="text-[11px] text-wb-text-muted mt-1 leading-snug line-clamp-2">
                  {desc}
                </p>
              </div>

              <div className="mt-2.5 pt-2 border-t border-wb-border/60 flex items-center justify-between text-[10px] text-wb-amber-700 font-semibold">
                <span>{isBn ? 'সহায়তা ডেস্কে জিজ্ঞাসা করুন' : 'Ask Sahayata Desk'}</span>
                <span>→</span>
              </div>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
