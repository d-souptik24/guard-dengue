/**
 * AppShell — Main application shell for GuardDengue
 *
 * Implements:
 * - West Bengal Government / Swasthya Bhawan institutional header
 * - Emergency Helpline quick-dial badge
 * - Bilingual Language Switcher (EN / বাংলা)
 * - Academic "Inspector Mode" Toggle for Dr. Wazib & Viva evaluation
 * - Full-width, properly centered responsive grid (centered on wide monitors)
 * - Official statutory health awareness disclaimer footer
 */
import { type ReactNode } from 'react'
import { useSettings } from '@/store/settings'
import { EMERGENCY_CONTACTS } from '@/constants'
import {
  ShieldAlert,
  PhoneCall,
  Activity,
  HeartPulse,
} from 'lucide-react'

interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const { settings, setLanguage, toggleInspector } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <div
      className="min-h-screen flex flex-col w-full bg-slate-50 text-slate-800 antialiased selection:bg-teal-100 selection:text-teal-900"
      data-lang={settings.language}
    >
      {/* ─── Top Government Affiliation Bar ──────────────────────────── */}
      <div className="w-full bg-slate-900 text-slate-300 text-xs py-1.5 px-4 border-b border-slate-800">
        <div className="max-w-5xl mx-auto flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse shrink-0" />
            <span className="font-medium text-slate-200">
              {isBn
                ? 'পশ্চিমবঙ্গ সরকার • স্বাস্থ্য ও পরিবার কল্যাণ দপ্তর'
                : 'Government of West Bengal • Department of Health & Family Welfare'}
            </span>
          </div>
          <div className="flex items-center gap-3 text-slate-400 text-xs">
            <span>Swasthya Bhawan Initiative</span>
            <span className="hidden sm:inline">•</span>
            <span className="hidden sm:inline font-mono">Academic B.Tech IT Project</span>
          </div>
        </div>
      </div>

      {/* ─── Main Navigation Header ──────────────────────────────────── */}
      <header className="w-full sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200 shadow-xs">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between gap-3">
          {/* Brand & Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-900 via-indigo-900 to-teal-800 flex items-center justify-center text-white shadow-md shadow-blue-950/20 ring-1 ring-white/20 shrink-0">
              <ShieldAlert className="w-5 h-5 text-teal-300" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-bold text-slate-900 tracking-tight leading-none">
                  Guard<span className="text-teal-700">Dengue</span>
                </span>
                <span className="px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider bg-teal-50 text-teal-800 rounded border border-teal-200">
                  SLM v2
                </span>
              </div>
              <p className="text-xs text-slate-500 font-normal leading-tight mt-0.5">
                {isBn
                  ? 'তথ্যভিত্তিক ডেঙ্গু স্বাস্থ্য সচেতনতা ব্যবস্থা'
                  : 'Safety-Aware Dengue Health Awareness'}
              </p>
            </div>
          </div>

          {/* Action Controls */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            {/* Emergency Helpline Pill */}
            <a
              href={`tel:${EMERGENCY_CONTACTS.stateHealth}`}
              className="hidden md:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-50 text-red-700 border border-red-200 hover:bg-red-100 transition-colors shadow-xs"
              title="State Health Helpline"
            >
              <PhoneCall className="w-3.5 h-3.5 text-red-600 animate-bounce" />
              <span>
                {isBn ? 'হেল্পলাইন:' : 'Helpline:'}{' '}
                <strong className="font-mono">{EMERGENCY_CONTACTS.stateHealth}</strong>
              </span>
            </a>

            {/* Bilingual Toggle */}
            <div
              role="group"
              aria-label="Language selection"
              className="inline-flex p-1 rounded-lg bg-slate-100 border border-slate-200 text-xs font-medium"
            >
              <button
                type="button"
                onClick={() => setLanguage('en')}
                className={`px-2.5 py-1 rounded-md transition-all min-h-[30px] cursor-pointer ${
                  !isBn
                    ? 'bg-white text-blue-900 font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                aria-pressed={!isBn}
              >
                EN
              </button>
              <button
                type="button"
                onClick={() => setLanguage('bn')}
                className={`px-2.5 py-1 rounded-md transition-all min-h-[30px] cursor-pointer ${
                  isBn
                    ? 'bg-white text-blue-900 font-semibold shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                aria-pressed={isBn}
              >
                বাংলা
              </button>
            </div>

            {/* Inspector Mode Toggle (Viva / Dr. Wazib Trace Panel) */}
            <button
              type="button"
              onClick={toggleInspector}
              className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all cursor-pointer min-h-[36px] ${
                settings.inspectorMode
                  ? 'bg-indigo-900 text-white border-indigo-900 shadow-sm ring-2 ring-indigo-300'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
              title="Toggle Clinical Trace & LangGraph Inspector Panel"
              aria-pressed={settings.inspectorMode}
            >
              <Activity
                className={`w-3.5 h-3.5 ${
                  settings.inspectorMode ? 'text-teal-300' : 'text-slate-500'
                }`}
              />
              <span className="hidden sm:inline">
                {isBn ? 'ইনস্পেক্টর' : 'Inspector'}
              </span>
              <span
                className={`w-2 h-2 rounded-full ${
                  settings.inspectorMode ? 'bg-teal-400' : 'bg-slate-300'
                }`}
              />
            </button>
          </div>
        </div>
      </header>

      {/* ─── Main Content Canvas (Horizontally Centered) ─────────────── */}
      <main className="flex-1 w-full max-w-5xl mx-auto px-4 sm:px-6 py-6 flex flex-col">
        {children}
      </main>

      {/* ─── Institutional Health Disclaimer Footer ──────────────────── */}
      <footer className="w-full bg-white border-t border-slate-200 mt-auto py-5 px-4 text-xs text-slate-600">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-start gap-2 max-w-2xl text-center md:text-left">
            <HeartPulse className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
            <p className="text-[11px] leading-relaxed text-slate-500">
              <strong>
                {isBn ? 'বিধিবদ্ধ স্বাস্থ্য সতর্কতা:' : 'Statutory Medical Disclaimer:'}
              </strong>{' '}
              {isBn
                ? 'গার্ডডেঙ্গু শুধুমাত্র প্রাতিষ্ঠানিক তথ্যভিত্তিক সচেতনতার উদ্দেশ্যে তৈরি। এটি কোনোভাবেই চিকিৎসাগত রোগ নির্ণয় (diagnosis), ব্যক্তিগত ওষুধ ব্যবস্থাপত্র (prescription) বা স্বয়ংক্রিয় ক্লিনিক্যাল ট্রায়াজ প্রদান করে না। যেকোনো জটিল বা জরুরি উপসর্গে নিকটস্থ সরকারি স্বাস্থ্যকেন্দ্র বা চিকিৎসকের পরামর্শ নিন।'
                : 'GuardDengue provides evidence-grounded health education and awareness only. It does not provide medical diagnosis, personalized drug prescriptions, or clinical triage. For severe symptoms or emergencies, immediately consult a registered medical professional or visit the nearest hospital.'}
            </p>
          </div>

          <div className="flex items-center gap-3 shrink-0 text-slate-500 text-[11px]">
            <span>WB Health: <strong>1800-313444-222</strong></span>
            <span>•</span>
            <span>Ambulance: <strong>108</strong></span>
          </div>
        </div>
      </footer>
    </div>
  )
}
