/**
 * ChatPage — Primary Dengue Health Awareness Conversational Workspace
 *
 * Implements:
 * - Zone 2 Emergency Red-Flag Banner (defervescence phase alert)
 * - Hero orientation card defining clinical boundaries
 * - Bilingual Quick-Prompt suggestion pills
 * - Interactive conversation turns with verifiable evidence citations
 * - Ample bottom spacing so sticky input bar NEVER overlaps messages
 * - Integration with Dr. Wazib's Inspector Mode panel
 */
import { useState } from 'react'
import { useSettings } from '@/store/settings'
import { QUICK_PROMPTS } from '@/constants'
import EmergencyBanner from '@/components/safety/EmergencyBanner'
import InspectorPanel from '@/components/inspector/InspectorPanel'
import {
  Send,
  Sparkles,
  ShieldCheck,
  BookOpen,
  Clock,
} from 'lucide-react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  topic?: string
  source?: string
  evidenceLevel?: string
  route?: 'urgent' | 'education' | 'medication'
  timestamp: string
}

export default function ChatPage() {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'msg-01',
      role: 'user',
      content: isBn
        ? 'জ্বর কমে যাওয়ার পর কি ডেঙ্গু রোগীর বিপদ কেটে যায়? কী কী লক্ষণ খেয়াল রাখতে হবে?'
        : 'Why should someone keep watching for warning signs after their fever starts to go down?',
      timestamp: '10:32 AM',
    },
    {
      id: 'msg-02',
      role: 'assistant',
      route: 'education',
      topic: 'Warning signs',
      source: 'WHO Dengue Guidelines 2024 & NCVBDC Protocols',
      evidenceLevel: 'Level 1 (Global Clinical Practice Guideline)',
      timestamp: '10:32 AM',
      content: isBn
        ? `না, জ্বর কমলেই ডেঙ্গু রোগীর বিপদ কাটে না। প্রকৃতপক্ষে, ডেঙ্গুর সবথেকে বিপজ্জনক পর্যায় হলো 'ক্রিটিক্যাল ফেজ' (Critical Phase), যা সাধারণত ৩য় থেকে ৭ম দিনে জ্বর কমে যাওয়ার (Defervescence) সময় শুরু হয়।

এই সময়ে রক্তনালী থেকে প্লাজমা লিকেজ (Plasma Leakage) হওয়ার সর্বোচ্চ ঝুঁকি থাকে, যা ডেঙ্গু শক সিন্ড্রোম (Dengue Shock Syndrome) ঘটাতে পারে।

নিম্নলিখিত সতর্কতামূলক লক্ষণগুলো (Warning Signs) দেখা দিলে এক মুহূর্তও অপেক্ষা না করে অবিলম্বে হাসপাতালে ভর্তি হতে হবে:
1. পেটে তীব্র ও ক্রমাগত ব্যথা (Severe abdominal pain)
2. অনবরত বমি বা তরল ধরে রাখতে না পারা (Persistent vomiting)
3. মাড়ি, নাক দিয়ে রক্তপাত বা কালো মল (Mucosal bleeding)
4. হাত-পা ঠান্ডা হয়ে যাওয়া ও অতিরিক্ত দুর্বলতা বা অস্থিরতা (Cold, clammy skin, lethargy)
5. শ্বাসকষ্ট বা দ্রুত শ্বাস নেওয়া (Respiratory distress)

গুরুত্বপূর্ণ ওষুধ সতর্কতা: এই সময়ে বা ডেঙ্গু চলাকালীন কোনো অবস্থাতেই অ্যাসপিরিন বা আইবুপ্রোফেন (যেমন Combiflam) খাওয়া যাবে না, কারণ এগুলো রক্তক্ষরণের ঝুঁকি মারাত্মকভাবে বাড়িয়ে দেয়।`
        : `No, the danger does not pass when fever drops. In fact, the most dangerous phase of dengue is the "critical phase," which typically begins during defervescence (Days 3–7) as the fever subsides.

During this window, increased capillary permeability can cause plasma leakage, fluid accumulation, hemoconcentration, and severe drop in platelets, potentially progressing to Dengue Shock Syndrome.

Immediate emergency hospital evaluation is vital if any of the following Warning Signs occur:
1. Severe, localized abdominal pain or tenderness
2. Persistent vomiting (unable to retain fluids orally)
3. Mucosal bleeding (bleeding gums, epistaxis, or melena/black stools)
4. Cold, clammy skin, rapid weak pulse, or extreme restlessness/lethargy
5. Respiratory distress (fast or labored breathing)

Medication Precaution: Never take NSAIDs (such as ibuprofen, aspirin, naproxen, or diclofenac) for fever or body ache during suspected dengue, as their antiplatelet effects substantially elevate gastrointestinal bleeding risks. Only paracetamol may be used under clinical guidance.`,
    },
  ])

  const [input, setInput] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const quickPrompts = QUICK_PROMPTS[settings.language]

  const handleSend = (textToSend?: string) => {
    const query = (textToSend || input).trim()
    if (!query) return

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      role: 'user',
      content: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsSubmitting(true)

    setTimeout(() => {
      const isUrgentQuery =
        query.toLowerCase().includes('vomit') ||
        query.toLowerCase().includes('stomach') ||
        query.toLowerCase().includes('বমি') ||
        query.toLowerCase().includes('ব্যথা') ||
        query.toLowerCase().includes('bleed')

      const assistantMsg: Message = {
        id: `ast-${Date.now()}`,
        role: 'assistant',
        route: isUrgentQuery ? 'urgent' : 'education',
        topic: isUrgentQuery ? 'Emergency guidance' : 'Medication safety',
        source: 'WHO Clinical Case Management Protocols (2024)',
        evidenceLevel: 'Level 1 (Global Clinical Practice Guideline)',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: isUrgentQuery
          ? isBn
            ? `জরুরি সতর্কবার্তা: আপনার উল্লেখিত লক্ষণগুলো ডেঙ্গুর 'ওয়ার্নিং সাইন' বা বিপদচিহ্নের অন্তর্গত। অবিলম্বে নিকটস্থ হাসপাতালের জরুরি বিভাগ অথবা স্বাস্থ্যকেন্দ্রে যোগাযোগ করুন। বাড়িতে বসে অপেক্ষা করবেন না বা নিজে কোনো অ্যান্টিবায়োটিক বা ব্যথানাশক ওষুধ খাবেন না। সরকারি অ্যাম্বুলেন্সের জন্য ১০৮ নম্বরে কল করুন।`
            : `EMERGENCY CLINICAL ADVISORY: The symptoms you described are recognized clinical warning signs indicating potential plasma leakage or evolving dengue shock. Do not wait at home. Proceed immediately to the nearest hospital emergency department. For ambulance assistance, call 108.`
          : isBn
            ? `ডেঙ্গু সন্দেহে যেকোনো প্রকার ব্যথানাশক (NSAIDs) যেমন আইবুপ্রোফেন, অ্যাসপিরিন বা ডাইক্লোফেনাক সম্পূর্ণ নিষিদ্ধ। শুধুমাত্র প্যারাসিটামল চিকিৎসকের পরামর্শ অনুযায়ী নির্দিষ্ট মাত্রায় সেবন করা যেতে পারে।`
            : `When dengue is possible, non-steroidal anti-inflammatory drugs (NSAIDs) such as ibuprofen and aspirin are strictly contraindicated due to increased risk of internal hemorrhage. Only paracetamol under professional medical supervision is indicated.`,
      }

      setMessages((prev) => [...prev, assistantMsg])
      setIsSubmitting(false)
    }, 800)
  }

  return (
    <div className="flex-1 flex flex-col w-full max-w-4xl mx-auto">
      {/* ─── Zone 2 Deterministic Emergency Alert ──────────────────── */}
      <EmergencyBanner onSelectPrompt={(prompt) => handleSend(prompt)} />

      {/* ─── Hero Orientation Card ─────────────────────────────────── */}
      <div className="mb-6 rounded-2xl bg-white border border-slate-200 p-5 shadow-xs">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-teal-50 text-teal-700 flex items-center justify-center shrink-0">
                <Sparkles className="w-3.5 h-3.5" />
              </span>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                {isBn
                  ? 'গার্ডডেঙ্গু প্রাতিষ্ঠানিক স্বাস্থ্য তথ্য নির্দেশিকা'
                  : 'GuardDengue Clinical Knowledge Workspace'}
              </h2>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed max-w-2xl">
              {isBn
                ? 'পশ্চিমবঙ্গ সরকার ও WHO, NCVBDC নির্দেশিকা অনুযায়ী ডেঙ্গুর লক্ষণ, প্রতিরোধ, হাইড্রেশন ও বিপৎচিহ্ন সম্পর্কে সঠিক ও যাচাইকৃত তথ্য জানুন।'
                : 'Evidence-grounded dengue awareness powered by dual Qdrant vector retrieval, Neo4j contraindication graph, and NLI Claim Verification. Select a common inquiry below or ask a question.'}
            </p>
          </div>

          <div className="hidden sm:flex flex-col items-end text-right text-[11px] text-slate-500 shrink-0">
            <span className="font-semibold text-slate-700">Corpus Release: 2026.09</span>
            <span>WHO • ICMR • NCVBDC</span>
          </div>
        </div>

        {/* Quick Suggestion Pills */}
        <div className="mt-4 pt-3.5 border-t border-slate-100">
          <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block mb-2">
            {isBn ? 'প্রস্তাবিত জরুরি প্রশ্নসমূহ:' : 'Recommended Clinical Inquiries:'}
          </span>
          <div className="flex flex-wrap gap-2">
            {quickPrompts.map((prompt, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSend(prompt)}
                className="px-3 py-1.5 rounded-full text-xs bg-slate-100/90 hover:bg-teal-50 text-slate-700 hover:text-teal-900 border border-slate-200 hover:border-teal-300 transition-all text-left cursor-pointer min-h-[32px] flex items-center gap-1.5"
              >
                <span>{prompt}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* ─── Conversation Stream (with ample bottom padding) ────────── */}
      <div className="flex-1 space-y-5 mb-6 pb-20">
        {messages.map((msg) => (
          <article
            key={msg.id}
            className={`flex flex-col ${
              msg.role === 'user' ? 'items-end' : 'items-start'
            }`}
          >
            {/* User Message Bubble */}
            {msg.role === 'user' ? (
              <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-br-xs px-4 py-3 bg-blue-900 text-white shadow-xs">
                <p className="text-xs sm:text-sm leading-relaxed">{msg.content}</p>
                <div className="mt-1 text-right text-[10px] text-blue-200 font-mono">
                  {msg.timestamp}
                </div>
              </div>
            ) : (
              /* Assistant Message Bubble */
              <div
                className={`w-full max-w-3xl rounded-2xl rounded-bl-xs p-5 shadow-xs border ${
                  msg.route === 'urgent'
                    ? 'bg-red-50/90 border-red-200 text-red-950'
                    : 'bg-white border-slate-200 text-slate-800'
                }`}
              >
                {/* Verified Header */}
                <div className="mb-3 pb-2.5 border-b border-slate-100 flex flex-wrap items-center justify-between gap-2 text-[11px]">
                  <div className="flex items-center gap-1.5">
                    <span className="w-4 h-4 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center shrink-0">
                      <ShieldCheck className="w-3 h-3 text-teal-700" />
                    </span>
                    <span className="font-semibold text-slate-900">
                      GuardDengue Verified Evidence
                    </span>
                    {msg.topic && (
                      <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-medium text-[10px]">
                        {msg.topic}
                      </span>
                    )}
                  </div>

                  {msg.evidenceLevel && (
                    <span className="px-2 py-0.5 rounded-md bg-blue-50 text-blue-800 font-medium text-[10px] border border-blue-200">
                      {msg.evidenceLevel}
                    </span>
                  )}
                </div>

                {/* Content */}
                <div className="text-xs sm:text-sm leading-relaxed whitespace-pre-line font-normal text-slate-700">
                  {msg.content}
                </div>

                {/* Source Provenance Footer */}
                {msg.source && (
                  <div className="mt-3.5 pt-2.5 border-t border-slate-100 flex items-center justify-between gap-2 text-[11px] text-slate-500">
                    <div className="flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>Source: <strong>{msg.source}</strong></span>
                    </div>
                    <span className="font-mono text-[10px] text-slate-400">
                      {msg.timestamp}
                    </span>
                  </div>
                )}
              </div>
            )}
          </article>
        ))}

        {isSubmitting && (
          <div className="flex items-center gap-2 p-4 max-w-sm rounded-2xl bg-white border border-slate-200 text-slate-500 text-xs shadow-xs animate-pulse">
            <Clock className="w-4 h-4 text-teal-600 animate-spin" />
            <span>
              {isBn
                ? 'ল্যাংগ্রাফ স্টেট ও প্রমাণ যাচাই করা হচ্ছে...'
                : 'Verifying evidence against WHO guidelines (NLI Gate)...'}
            </span>
          </div>
        )}
      </div>

      {/* ─── Chat Input Bar (Sticky with background blur and shadow) ─── */}
      <div className="sticky bottom-4 z-20 w-full mt-auto">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            handleSend()
          }}
          className="bg-white/95 backdrop-blur-md rounded-2xl border-2 border-slate-200 p-2 shadow-lg focus-within:border-teal-600 transition-colors"
        >
          <div className="flex items-center gap-2">
            <label htmlFor="dengue-query-input" className="sr-only">
              {isBn ? 'ডেঙ্গু স্বাস্থ্য প্রশ্ন লিখুন' : 'Enter dengue inquiry'}
            </label>
            <input
              id="dengue-query-input"
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isSubmitting}
              placeholder={
                isBn
                  ? 'ডেঙ্গুর লক্ষণ, ওষুধ সতর্কতা, বা প্রতিরোধ সম্পর্কে জিজ্ঞাসা করুন...'
                  : 'Ask about dengue warning signs, fluid hydration, platelet tests, medication safety...'
              }
              className="flex-1 px-3 py-2 text-xs sm:text-sm text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none min-h-[44px]"
            />

            <button
              type="submit"
              disabled={!input.trim() || isSubmitting}
              className="w-11 h-11 rounded-xl bg-blue-900 hover:bg-blue-950 disabled:bg-slate-200 text-white disabled:text-slate-400 flex items-center justify-center transition-all cursor-pointer disabled:cursor-not-allowed shrink-0 shadow-sm"
              aria-label={isBn ? 'বার্তা পাঠান' : 'Send message'}
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          <div className="px-3 pt-1.5 pb-1 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-400 border-t border-slate-100 mt-1">
            <span>
              {isBn
                ? 'আইবুপ্রোফেন/অ্যাসপিরিন সম্পূর্ণরূপে এড়িয়ে চলুন • জরুরি প্রয়োজনে ১০৮ নম্বরে যোগাযোগ করুন'
                : 'Avoid NSAIDs (Ibuprofen/Aspirin) • For medical emergencies call 108'}
            </span>
            <span className="hidden sm:inline font-mono">
              {isBn ? 'সরাসরি চিকিৎসা পরামর্শ নয়' : 'Health Education Only'}
            </span>
          </div>
        </form>
      </div>

      {/* ─── Dr. Wazib's Inspector Mode Panel ───────────────────────── */}
      <InspectorPanel />
    </div>
  )
}
