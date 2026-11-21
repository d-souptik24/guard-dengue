/**
 * AboutPage — Academic Prototype Disclosure, Clinical Governance & Research Team
 *
 * Grounded directly in University of Calcutta & WB Health Initiative:
 * - Institutional Affiliation: A. K. Choudhury School of Information Technology (A.K.C.S.I.T.), University of Calcutta
 * - Proposed for: Department of Health & Family Welfare, Government of West Bengal
 * -Faculty Supervisor: Prof. (Dr.) Amlan Chakraborty (Director & Professor, A.K.C.S.I.T.)
 * - Research Co-Supervisors / Mentors:
 *   - Dr. Wazib (LLM/SLM & RAG Systems Architecture)
 *   - Dr. Jhilam (Health Data Analytics & Clinical Evaluation)
 * - Student Researchers (B.Tech, A.K.C.S.I.T.):
 *   - Souptik Dutta, Ayan Chakraborty, Rupchand Naiya, Swarnajit Paul
 * - Clinical Authority Guidelines: WHO (2024), ICMR, NCVBDC, WB Health
 * - AI Safety Foundations: Amugongo et al. (PLOS 2025), Basu & Huynh (BMC 2026)
 */
import { Link } from 'react-router-dom'
import {
  Award,
  BookOpen,
  ArrowLeft,
  GraduationCap,
  Scale,
  ExternalLink,
} from 'lucide-react'
import { useSettings } from '@/store/settings'

export default function AboutPage() {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  const contributors = [
    { name: 'Souptik Dutta', github: 'd-souptik24', url: 'https://github.com/d-souptik24' },
    { name: 'Ayan Chakraborty', github: 'Ayan-chakraborty255', url: 'https://github.com/Ayan-chakraborty255' },
    { name: 'Rupchand Naiya', github: 'usergithubrup', url: 'https://github.com/usergithubrup' },
    { name: 'Swarnajit Paul', github: 'swarnajit006', url: 'https://github.com/swarnajit006' },
  ]

  return (
    <div className="max-w-4xl mx-auto py-6 px-4 space-y-6 animate-in fade-in duration-300">
      {/* Return to Desk */}
      <div>
        <Link
          to="/"
          className="min-h-[44px] inline-flex items-center gap-2 text-xs sm:text-sm font-semibold text-wb-amber-700 hover:text-wb-ochre-800 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          <span>{isBn ? 'মূল সহায়তাকেন্দ্রে ফিরে যান' : 'Back to Sahayata Desk'}</span>
        </Link>
      </div>

      {/* Main Header Card */}
      <section className="bg-white rounded-2xl border border-wb-border p-6 sm:p-8 shadow-xs space-y-4">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 text-wb-amber-700 border border-amber-200">
          <GraduationCap className="w-4 h-4" aria-hidden="true" />
          <span>{isBn ? 'একাডেমিক গবেষণা প্রোটোটাইপ' : 'Academic Research Prototype'}</span>
        </div>

        <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 tracking-tight">
          Guard<span className="text-wb-amber-700">Dengue</span>
        </h1>

        <p className="text-sm sm:text-base text-slate-700 leading-relaxed max-w-3xl">
          {isBn
            ? 'গার্ডডেঙ্গু হলো কলকাতা বিশ্ববিদ্যালয়ের এ. কে. চৌধুরী স্কুল অফ ইনফরমেশন টেকনোলজি (A.K.C.S.I.T.) কর্তৃক প্রস্তাবিত একটি প্রমাণ-ভিত্তিক জনস্বাস্থ্য সচেতনতা ও তথ্য যাচাইকরণ ব্যবস্থা। এটি পশ্চিমবঙ্গ সরকারের স্বাস্থ্য ও পরিবার কল্যাণ দপ্তরের ক্লিনিক্যাল নির্দেশিকা অনুসারে জনস্বার্থে তৈরি একটি বি.টেক গবেষক দলের প্রকল্প।'
            : 'GuardDengue is an evidence-grounded public health awareness and clinical verification prototype developed at the A. K. Choudhury School of Information Technology (A.K.C.S.I.T.), University of Calcutta, proposed for the Department of Health & Family Welfare, Government of West Bengal.'}
        </p>
      </section>

      {/* Clean 2-Column Primary Details Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column: Academic Supervision & Team */}
        <section className="bg-white rounded-2xl border border-wb-border p-6 shadow-xs flex flex-col justify-between space-y-6">
          <div className="space-y-5">
            <div className="flex items-center gap-2.5 text-wb-amber-700 border-b border-slate-100 pb-3">
              <Award className="w-5 h-5" aria-hidden="true" />
              <h2 className="font-bold text-base text-slate-900">
                {isBn ? 'একাডেমিক তত্ত্বাবধান ও দল' : 'Academic Supervision & Team'}
              </h2>
            </div>

            {/* Lead Faculty Supervisor */}
            <div className="space-y-1">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-wb-amber-700 block">
                {isBn ? 'ফ্যাকাল্টি তত্ত্বাবধায়ক' : 'Faculty Supervisor'}
              </span>
              <p className="font-bold text-slate-900 text-sm sm:text-base">
                Prof. (Dr.) Amlan Chakraborty
              </p>
              <p className="text-xs text-slate-600">
                {isBn
                  ? 'পরিচালক ও অধ্যাপক, এ. কে. চৌধুরী স্কুল অফ ইনফরমেশন টেকনোলজি (A.K.C.S.I.T.), কলকাতা বিশ্ববিদ্যালয়'
                  : 'Director & Professor, A. K. Choudhury School of Information Technology (A.K.C.S.I.T.), University of Calcutta'}
              </p>
            </div>

            {/* Research Mentors / Co-Guides */}
            <div className="space-y-2.5 pt-1 border-t border-slate-100">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
                {isBn ? 'গবেষণা সহ-তত্ত্বাবধায়ক ও নির্দেশক' : 'Research Co-Guides & Mentors'}
              </span>
              <div className="space-y-2 text-xs sm:text-sm">
                <div>
                  <span className="font-semibold text-slate-900">Dr. Wazib</span>
                  <span className="text-slate-600 block text-xs">
                    {isBn ? 'LLM/SLM ও RAG সিস্টেমস আর্কিটেকচার' : 'LLM/SLM & RAG Systems Architecture'}
                  </span>
                </div>
                <div>
                  <span className="font-semibold text-slate-900">Dr. Jhilam</span>
                  <span className="text-slate-600 block text-xs">
                    {isBn ? 'স্বাস্থ্য ডেটা অ্যানালিটিক্স ও ক্লিনিক্যাল মূল্যায়ন' : 'Health Data Analytics & Clinical Evaluation'}
                  </span>
                </div>
              </div>
            </div>

            {/* Student Researchers */}
            <div className="space-y-2 pt-1 border-t border-slate-100">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
                {isBn ? 'ছাত্র গবেষক দল (বি.টেক, A.K.C.S.I.T.)' : 'Student Researchers (B.Tech, A.K.C.S.I.T.)'}
              </span>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {contributors.map((c) => (
                  <a
                    key={c.github}
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-slate-800 hover:text-wb-amber-700 transition-colors py-1 font-medium group"
                  >
                    <span>{c.name}</span>
                    <ExternalLink className="w-3 h-3 text-slate-400 group-hover:text-wb-amber-700" aria-hidden="true" />
                  </a>
                ))}
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 font-mono">
            A.K.C.S.I.T., University of Calcutta
          </div>
        </section>

        {/* Right Column: Clinical Authorities & Scientific Grounding */}
        <section className="bg-white rounded-2xl border border-wb-border p-6 shadow-xs flex flex-col justify-between space-y-6">
          <div className="space-y-5">
            <div className="flex items-center gap-2.5 text-wb-teal-evidence border-b border-slate-100 pb-3">
              <BookOpen className="w-5 h-5" aria-hidden="true" />
              <h2 className="font-bold text-base text-slate-900">
                {isBn ? 'ক্লিনিক্যাল সূত্র ও বৈজ্ঞানিক ভিত্তি' : 'Clinical Authority & Research Grounding'}
              </h2>
            </div>

            {/* Official Practice Guidelines */}
            <div className="space-y-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-wb-teal-evidence block">
                {isBn ? 'অনুমোদিত ক্লিনিক্যাল প্রোটোকল' : 'Statutory Clinical Protocols'}
              </span>
              <ul className="text-xs sm:text-sm text-slate-700 space-y-2">
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-wb-teal-evidence mt-1.5 shrink-0" aria-hidden="true" />
                  <span>World Health Organization (WHO) Dengue Guidelines (2024)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-wb-teal-evidence mt-1.5 shrink-0" aria-hidden="true" />
                  <span>Indian Council of Medical Research (ICMR) Laboratory Protocol</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-wb-teal-evidence mt-1.5 shrink-0" aria-hidden="true" />
                  <span>National Center for Vector Borne Diseases Control (NCVBDC)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-wb-teal-evidence mt-1.5 shrink-0" aria-hidden="true" />
                  <span>Dept. of Health & Family Welfare, Govt. of West Bengal</span>
                </li>
              </ul>
            </div>

            {/* AI Safety Grounding */}
            <div className="space-y-2.5 pt-1 border-t border-slate-100">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block">
                {isBn ? 'যাচাইকরণ গবেষণা ভিত্তি' : 'Clinical AI Verification Literature'}
              </span>
              <div className="space-y-2 text-xs text-slate-700">
                <div>
                  <strong className="text-slate-900 block font-semibold">Basu & Huynh (BMC Health Services Research, 2026)</strong>
                  <span className="text-[11px] text-slate-600 block mt-0.5">
                    {isBn
                      ? 'স্বাস্থ্যসেবায় ৩-স্তরীয় এআই হ্যালুসিনেশন ট্যাক্সোনমি (ইনপুট, কনটেক্সট ও ফ্যাক্ট দ্বন্দ্ব যাচাই)'
                      : '3-tier clinical hallucination taxonomy: Input, Context, and Fact conflict auditing'}
                  </span>
                </div>
                <div>
                  <strong className="text-slate-900 block font-semibold">Amugongo et al. (PLOS Digital Health, 2025)</strong>
                  <span className="text-[11px] text-slate-600 block mt-0.5">
                    {isBn
                      ? 'ক্লিনিক্যাল প্রেক্ষিতে আনস্ট্রাকচার্ড RAG দুর্বলতা ও অবধারিত সেফটি গেট'
                      : 'RAG vulnerabilities in clinical contexts and deterministic safety pathways'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-slate-100 text-[11px] text-slate-500 font-mono">
            Peer-Reviewed Medical AI Safety Standards
          </div>
        </section>
      </div>

      {/* Statutory Disclaimer */}
      <section className="bg-amber-50/80 rounded-2xl border border-amber-200 p-6 shadow-xs space-y-3 text-amber-950">
        <div className="flex items-center gap-2.5 font-bold text-sm text-amber-900">
          <Scale className="w-5 h-5 text-amber-700" aria-hidden="true" />
          <span>{isBn ? 'আইনগত ও সংবিধিবদ্ধ অস্বীকৃতি (Statutory Disclaimer)' : 'Statutory & Medical Disclaimer'}</span>
        </div>
        <p className="text-xs sm:text-sm leading-relaxed text-amber-900">
          {isBn
            ? 'গার্ডডেঙ্গু একটি বিশুদ্ধ একাডেমিক স্বাস্থ্য শিক্ষা প্রোটোটাইপ। এটি কোনোভাবেই একজন নিবন্ধিত ডাক্তারের বিকল্প নয়। এটি সরাসরি রোগ নির্ণয়, ব্যবস্থাপত্র প্রদান বা চিকিৎসার পরামর্শ দেয় না। যে কোনো তীব্র লক্ষণে অবিলম্বে ১০৮ / ১০২ নম্বরে অ্যাম্বুলেন্স ডাকুন অথবা নিকটবর্তী হাসপাতালে যান।'
            : 'GuardDengue is an academic public health educational prototype. It does NOT provide individualized clinical diagnosis, prescribe medication, or replace the professional judgment of a registered medical practitioner. In any acute or worsening symptom state, immediately call 108 / 102 or proceed to a hospital Emergency Department.'}
        </p>
      </section>
    </div>
  )
}
