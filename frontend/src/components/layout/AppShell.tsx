/**
 * AppShell — West Bengal Health Saffron Masthead & Application Shell
 *
 * Implements:
 * - GIGW 3.0 accessibility toolbar at root top
 * - Warm saffron masthead with deep ochre accent inspired by wbhealth.gov.in
 * - Custom GuardDengue health shield and bilingual department identity
 * - Explicit "Academic Research Prototype" disclosure badge
 * - One-tap emergency telephony quick-dial hub (108/102 & 1800-313-444-222)
 * - Supervisor Clinical Inspector toggle for Dr. Wazib and viva examiners
 * - Centered responsive container with <main id="main-content" tabIndex={-1}>
 * - Official civic footer with statutory non-diagnostic disclaimer
 */
import { type ReactNode } from 'react'
import { NavLink } from 'react-router-dom'
import { useSettings } from '@/store/settings'
import GIGWToolbar from './GIGWToolbar'
import GovFooter from './GovFooter'
import TelephonyBadge from '@/components/citizen/TelephonyBadge'
import InspectorPanel from '@/components/inspector/InspectorPanel'
import { Activity, MessageSquare, BookOpen, Info } from 'lucide-react'

export interface AppShellProps {
  children: ReactNode
}

export default function AppShell({ children }: AppShellProps) {
  const { settings, toggleInspector } = useSettings()
  const isBn = settings.language === 'bn'

  return (
    <div className="min-h-screen flex flex-col w-full bg-wb-canvas text-wb-text-main antialiased">
      {/* 1. GIGW Top Accessibility Strip */}
      <GIGWToolbar />

      {/* 2. West Bengal Health Saffron Masthead */}
      <header className="w-full bg-gradient-to-r from-wb-amber-600 via-wb-amber-700 to-wb-ochre-800 text-white shadow-md border-b-4 border-wb-ochre-900">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex flex-col md:flex-row items-center justify-between gap-4">
          {/* Left Column: Brand Identity & Academic Disclosure */}
          <div className="flex items-center gap-3.5 text-center md:text-left">
            <img
              src="/guarddengue_wb_emblem.svg?v=2.1"
              alt="GuardDengue Health Shield"
              className="w-12 h-12 shrink-0 drop-shadow-xs"
            />
            <div>
              <div className="flex flex-wrap items-center justify-center md:justify-start gap-2">
                <span className="text-base sm:text-lg font-bold tracking-tight text-white leading-tight">
                  Guard<span className="text-amber-200">Dengue</span>
                </span>
                <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-wb-ochre-900/70 text-amber-100 border border-amber-400/30">
                  {isBn ? 'গবেষণামূলক প্রোটোটাইপ' : 'Academic Research Prototype'}
                </span>
              </div>
              <p className="text-xs text-amber-100 font-medium leading-tight mt-0.5">
                {isBn
                  ? 'স্বাস্থ্য ও পরিবার কল্যাণ দপ্তর, পশ্চিমবঙ্গ সরকারের জন্য প্রস্তাবিত'
                  : 'Proposed for Dept. of Health & Family Welfare — Govt. of West Bengal'}
              </p>
              <p className="text-[10px] text-amber-200/90 font-mono hidden sm:block">
                A.K.C.S.I.T., University of Calcutta
              </p>
            </div>
          </div>

          {/* Right Column: Civic Telephony Hub & Inspector Toggle */}
          <div className="flex items-center gap-2 sm:gap-3 shrink-0">
            <TelephonyBadge />

            {/* Clinical Inspector Supervisor Toggle (Dr. Wazib & Examiners) */}
            <button
              type="button"
              onClick={toggleInspector}
              aria-pressed={settings.inspectorMode}
              title="Toggle Clinical Trace & LangGraph Inspector Panel"
              className={`min-h-[44px] inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all cursor-pointer ${
                settings.inspectorMode
                  ? 'bg-wb-ochre-900 text-white border-amber-300 shadow-sm ring-2 ring-amber-300'
                  : 'bg-white/10 text-white border-white/20 hover:bg-white/20'
              }`}
            >
              <Activity
                className={`w-4 h-4 ${
                  settings.inspectorMode ? 'text-amber-300' : 'text-amber-100'
                }`}
                aria-hidden="true"
              />
              <span className="hidden sm:inline">
                {isBn ? 'ইনস্পেক্টর' : 'Inspector'}
              </span>
              <span
                className={`w-2 h-2 rounded-full ${
                  settings.inspectorMode ? 'bg-amber-300 animate-pulse' : 'bg-white/40'
                }`}
                aria-hidden="true"
              />
            </button>
          </div>
        </div>
      </header>

      {/* 2.5. Primary Navigation Strip */}
      <nav aria-label={isBn ? 'প্রধান নেভিগেশন' : 'Primary Navigation'} className="w-full bg-white border-b border-wb-border shadow-2xs">
        <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 flex items-center gap-1 sm:gap-2">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `min-h-[44px] inline-flex items-center gap-2 px-3 sm:px-4 py-2.5 text-xs sm:text-sm font-semibold border-b-2 transition-colors ${
                isActive
                  ? 'border-wb-amber-700 text-wb-amber-800 bg-amber-50/60'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
              }`
            }
          >
            <MessageSquare className="w-4 h-4" aria-hidden="true" />
            <span>{isBn ? 'সহায়তা ডেস্ক' : 'Sahayata Desk'}</span>
          </NavLink>

          <NavLink
            to="/guides"
            className={({ isActive }) =>
              `min-h-[44px] inline-flex items-center gap-2 px-3 sm:px-4 py-2.5 text-xs sm:text-sm font-semibold border-b-2 transition-colors ${
                isActive
                  ? 'border-wb-amber-700 text-wb-amber-800 bg-amber-50/60'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
              }`
            }
          >
            <BookOpen className="w-4 h-4" aria-hidden="true" />
            <span>{isBn ? 'ক্লিনিক্যাল নির্দেশিকা' : 'Clinical Guides'}</span>
          </NavLink>

          <NavLink
            to="/about"
            className={({ isActive }) =>
              `min-h-[44px] inline-flex items-center gap-2 px-3 sm:px-4 py-2.5 text-xs sm:text-sm font-semibold border-b-2 transition-colors ${
                isActive
                  ? 'border-wb-amber-700 text-wb-amber-800 bg-amber-50/60'
                  : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
              }`
            }
          >
            <Info className="w-4 h-4" aria-hidden="true" />
            <span>{isBn ? 'সম্পর্কে ও গভর্ন্যান্স' : 'About & Governance'}</span>
          </NavLink>
        </div>
      </nav>

      {/* 3. Primary Content (Above-the-fold workspace) */}
      <main id="main-content" tabIndex={-1} className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-4 sm:py-6 focus:outline-none">
        {children}
      </main>

      {/* 4. Official Government Footer */}
      <GovFooter />

      {/* 5. Supervisor Clinical Inspector Panel (Available across all routes) */}
      <InspectorPanel />
    </div>
  )
}
