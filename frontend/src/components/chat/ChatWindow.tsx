/**
 * ChatWindow — Bounded Scrollable Conversational Viewport
 *
 * Implements:
 * - Internal flex auto-scroll to latest turn
 * - Empty state with civic greeting & prompt pills
 * - Integrated TypingIndicator during pipeline execution
 * - WCAG 4.1.3 aria-live="polite" live status announcements
 */
import { useEffect, useRef } from 'react'
import type { ChatMessage } from '@/types'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'
import { ShieldCheck } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface ChatWindowProps {
  messages: ChatMessage[]
  isLoading?: boolean
  loadingStage?: 'screening' | 'verifying'
  className?: string
}

export default function ChatWindow({
  messages,
  isLoading = false,
  loadingStage = 'verifying',
  className = '',
}: ChatWindowProps) {
  const scrollRef = useRef<HTMLDivElement>(null)
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  // Auto-scroll to bottom on new message
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth',
      })
    }
  }, [messages, isLoading])

  return (
    <div
      ref={scrollRef}
      role="status"
      aria-live="polite"
      className={`flex-1 overflow-y-auto space-y-4 pr-1 pt-2 scroll-smooth focus:outline-none ${className}`}
      tabIndex={0}
      aria-label={isBn ? 'কথোপকথনের বার্তা তালিকা' : 'Conversation message stream'}
    >
      {messages.length === 0 ? (
        <div className="h-full min-h-[300px] flex flex-col items-center justify-center text-center p-6 text-slate-500 space-y-3.5 my-auto">
          <div className="w-12 h-12 rounded-2xl bg-amber-50 text-wb-amber-700 border border-amber-200 flex items-center justify-center shadow-2xs">
            <ShieldCheck className="w-6 h-6" aria-hidden="true" />
          </div>
          <div className="space-y-2 max-w-md">
            <h3 className="font-bold text-sm sm:text-base text-slate-800 tracking-tight">
              {isBn ? 'পশ্চিমবঙ্গ ডেঙ্গু সহায়তা ডেস্কে স্বাগতম' : 'Welcome to Dengue Health Sahayata Desk'}
            </h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {isBn
                ? 'গার্ডডেঙ্গু একটি স্বাস্থ্য সচেতনতামূলক শিক্ষা নির্দেশিকা, যা বিশ্ব স্বাস্থ্য সংস্থা (WHO) ও আইসিএমআর (ICMR) নির্দেশিকার ওপর ভিত্তি করে তৈরি। এটি কোনো চিকিৎসকের বিকল্প বা প্রেসক্রিপশন নয়।'
                : 'GuardDengue provides evidence-grounded health awareness aligned with WHO 2024 and ICMR protocols. It helps identify warning signs and safe care, but does not replace professional clinical diagnosis.'}
            </p>
          </div>
          <div className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-teal-800 bg-teal-50 px-3 py-1 rounded-full border border-teal-200">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" aria-hidden="true" />
            <span>WHO 2024 • ICMR Guidelines Grounded</span>
          </div>
        </div>
      ) : (
        messages.map((msg) => <MessageBubble key={msg.id} message={msg} />)
      )}

      {isLoading && (
        <div className="flex justify-start">
          <TypingIndicator stage={loadingStage} />
        </div>
      )}
    </div>
  )
}
