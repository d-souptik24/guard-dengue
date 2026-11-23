/**
 * MessageBubble — Outcome-Aware Conversational Turn
 *
 * Implements the 4 LangGraph outcome cards defined in design.md §5:
 *   1. Urgent (Zone 2 Emergency): Crimson alert, 108 ambulance dialer, EmergencyDialog
 *   2. Medication (Zone 2 NSAID Intercept): Amber warning, MedicationWarning modal trigger
 *   3. Education (Zone 4/5 Verified RAG): Pure white card, VerificationBadge, CitationAccordion
 *   4. Uncertain (Zone 2/5 Safe Abstain): SafeAbstainCard with 1800-313-444-222 helpline
 */
import { useState } from 'react'
import type { ChatMessage } from '@/types'
import {
  AlertTriangle,
  Pill,
  PhoneCall,
  ExternalLink,
  ShieldCheck,
  Clock,
} from 'lucide-react'
import VerificationBadge from '@/components/evidence/VerificationBadge'
import CitationAccordion from '@/components/evidence/CitationAccordion'
import EmergencyDialog from '@/components/safety/EmergencyDialog'
import MedicationWarning from '@/components/safety/MedicationWarning'
import SafeAbstainCard from '@/components/safety/SafeAbstainCard'
import MarkdownContent from './MarkdownContent'
import { useSettings } from '@/store/settings'

export interface MessageBubbleProps {
  message: ChatMessage
  className?: string
}

export default function MessageBubble({ message, className = '' }: MessageBubbleProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'
  const isUser = message.role === 'user'

  const [emergencyOpen, setEmergencyOpen] = useState(false)
  const [medicationOpen, setMedicationOpen] = useState(false)

  // User Message
  if (isUser) {
    return (
      <div className={`flex justify-end w-full ${className}`}>
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-br-xs px-4 py-2.5 bg-wb-amber-700 text-white shadow-xs">
          <p className="text-xs sm:text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
          <div className="mt-1 text-right text-[10px] text-amber-200/90 font-mono flex items-center justify-end gap-1">
            <Clock className="w-2.5 h-2.5" aria-hidden="true" />
            <span>{message.timestamp}</span>
          </div>
        </div>
      </div>
    )
  }

  // Assistant Message
  const resp = message.response
  const route = resp?.route || 'education'
  const verdict = resp?.verdict || 'pass'
  const evidence = resp?.evidence || []

  // 1. Uncertain / Out-of-Scope Route
  if (route === 'uncertain') {
    return (
      <div className={`w-full ${className}`}>
        <SafeAbstainCard reason={resp?.answer} />
      </div>
    )
  }

  // 2. Urgent Emergency Route
  if (route === 'urgent') {
    return (
      <div className={`w-full rounded-2xl rounded-bl-xs p-4 sm:p-5 shadow-xs border-2 border-red-300 bg-red-50/90 text-red-950 space-y-3 ${className}`}>
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-red-200">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600 animate-pulse" aria-hidden="true" />
            <h3 className="text-xs sm:text-sm font-bold text-red-900">
              {isBn ? 'জরুরী সতর্কতা — ডেঙ্গু বিপদ সংকেত' : 'Critical Warning — Emergency Triage'}
            </h3>
          </div>
          <VerificationBadge verdict="template_bypass" />
        </div>

        <MarkdownContent
          content={message.content}
          className="text-red-950 font-medium"
        />

        {/* Emergency Call Action & Dialog Trigger */}
        <div className="pt-2 flex flex-wrap items-center gap-2.5">
          <a
            href="tel:108"
            className="min-h-[44px] px-4 py-2 rounded-xl bg-red-600 hover:bg-red-700 text-white font-bold text-xs sm:text-sm inline-flex items-center gap-2 shadow-xs transition-colors cursor-pointer"
          >
            <PhoneCall className="w-4 h-4 animate-bounce" aria-hidden="true" />
            <span>{isBn ? '১০৮ নম্বরে অ্যাম্বুলেন্স ডাকুন' : 'Call 108 Ambulance'}</span>
          </a>

          <button
            type="button"
            onClick={() => setEmergencyOpen(true)}
            className="min-h-[44px] px-3.5 py-2 rounded-xl bg-white hover:bg-red-100 text-red-800 border border-red-300 font-semibold text-xs inline-flex items-center gap-1.5 transition-colors cursor-pointer"
          >
            <span>{isBn ? 'বিপদ নির্দেশিকা দেখুন' : 'View Action Protocol'}</span>
            <ExternalLink className="w-3.5 h-3.5" aria-hidden="true" />
          </button>
        </div>

        {evidence.length > 0 && <CitationAccordion evidence={evidence} />}

        <EmergencyDialog
          open={emergencyOpen}
          onOpenChange={setEmergencyOpen}
          symptomSummary={message.content.slice(0, 120)}
        />
      </div>
    )
  }

  // 3. Medication Safety Route (NSAID Intercept)
  if (route === 'medication') {
    return (
      <div className={`w-full rounded-2xl rounded-bl-xs p-4 sm:p-5 shadow-xs border-2 border-amber-300 bg-amber-50/90 text-amber-950 space-y-3 ${className}`}>
        <div className="flex flex-wrap items-center justify-between gap-2 pb-2.5 border-b border-amber-200">
          <div className="flex items-center gap-2">
            <Pill className="w-5 h-5 text-amber-700" aria-hidden="true" />
            <h3 className="text-xs sm:text-sm font-bold text-amber-900">
              {isBn ? 'ওষুধ সতর্কতা — রক্তক্ষরণ প্রতিরোধ' : 'Medication Safety Alert — NSAID Hazard'}
            </h3>
          </div>
          <VerificationBadge verdict="template_bypass" />
        </div>

        <MarkdownContent
          content={message.content}
          className="text-amber-950"
        />

        {/* Medication Dialog Trigger */}
        <div className="pt-2 flex flex-wrap items-center gap-2.5">
          <button
            type="button"
            onClick={() => setMedicationOpen(true)}
            className="min-h-[44px] px-4 py-2 rounded-xl bg-wb-amber-700 hover:bg-wb-ochre-800 text-white font-bold text-xs sm:text-sm inline-flex items-center gap-2 shadow-xs transition-colors cursor-pointer"
          >
            <ShieldCheck className="w-4 h-4" aria-hidden="true" />
            <span>{isBn ? 'সম্পূর্ণ ওষুধ নির্দেশিকা দেখুন' : 'View Complete Safety Advisory'}</span>
          </button>
        </div>

        {evidence.length > 0 && <CitationAccordion evidence={evidence} />}

        <MedicationWarning
          open={medicationOpen}
          onOpenChange={setMedicationOpen}
        />
      </div>
    )
  }

  // 4. Default: Educational Verified Evidence Route
  return (
    <div className={`w-full rounded-2xl rounded-bl-xs p-4 sm:p-5 shadow-xs border border-wb-border bg-white text-slate-800 space-y-3 ${className}`}>
      {/* Evidence Certification Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-100 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-wb-teal-evidence animate-pulse" aria-hidden="true" />
          <h3 className="font-bold text-slate-900 text-xs sm:text-sm">
            {isBn ? 'যাচাইকৃত স্বাস্থ্য তথ্য' : 'Verified Clinical Evidence'}
          </h3>
        </div>
        <VerificationBadge verdict={verdict} score={resp?.verification_score} />
      </div>

      {/* Answer Content */}
      <MarkdownContent
        content={message.content}
        className="text-slate-800"
      />

      {/* Citation Accordion */}
      {evidence.length > 0 && <CitationAccordion evidence={evidence} />}

      {/* Statutory Disclaimer Footer */}
      <div className="pt-2 text-[10px] text-slate-400 border-t border-slate-100 flex flex-wrap items-center justify-between gap-2 font-mono">
        <span>
          {isBn
            ? 'সরকারি স্বাস্থ্য নির্দেশিকা (WHO • ICMR 2024)'
            : 'Clinical Guidelines (WHO 2024 • ICMR Protocol)'}
        </span>
        <span>
          {resp?.attempts !== undefined && resp.attempts > 0
            ? `Revised (${resp.attempts}x)`
            : 'Directly Grounded'}
        </span>
      </div>
    </div>
  )
}
