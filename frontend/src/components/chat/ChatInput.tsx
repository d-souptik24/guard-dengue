/**
 * ChatInput — Accessible Civic Input Dock
 *
 * Implements:
 * - 52px accessible input dock with character counter (max 500 chars)
 * - WCAG 2.1 AA min-h-[44px] min-w-[44px] send button
 * - Enter key submission (with Shift+Enter for multiline)
 * - Clear button
 * - Mandatory non-diagnostic health education disclosure footer
 */
import { useState, useRef, type FormEvent, type KeyboardEvent } from 'react'
import { Send, XCircle } from 'lucide-react'
import { useSettings } from '@/store/settings'

export interface ChatInputProps {
  onSendMessage: (content: string) => void
  disabled?: boolean
  placeholder?: string
  className?: string
}

const MAX_CHARS = 500

export default function ChatInput({
  onSendMessage,
  disabled = false,
  placeholder,
  className = '',
}: ChatInputProps) {
  const [input, setInput] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  const defaultPlaceholder = isBn
    ? 'ডেঙ্গুর লক্ষণ, ওষুধ সুরক্ষা বা সতর্ক সংকেত সম্পর্কে লিখুন...'
    : 'Ask about dengue warning signs, paracetamol, hydration...'

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed || disabled) return
    onSendMessage(trimmed)
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const handleClear = () => {
    setInput('')
    if (textareaRef.current) {
      textareaRef.current.focus()
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className={`bg-white rounded-2xl border border-wb-border shadow-xs focus-within:ring-2 focus-within:ring-wb-amber-500 focus-within:border-wb-amber-500 transition-all ${className}`}
    >
      <div className="flex items-center gap-2 p-2 sm:p-2.5">
        <textarea
          ref={textareaRef}
          value={input}
          maxLength={MAX_CHARS}
          disabled={disabled}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={1}
          placeholder={placeholder || defaultPlaceholder}
          aria-label={isBn ? 'আপনার স্বাস্থ্য জিজ্ঞাসা লিখুন' : 'Enter health inquiry'}
          className="flex-1 max-h-32 min-h-[44px] resize-none bg-transparent px-2 py-2 text-xs sm:text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none disabled:opacity-50 font-sans"
        />

        {input.length > 0 && !disabled && (
          <button
            type="button"
            onClick={handleClear}
            className="min-h-[44px] min-w-[44px] flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors cursor-pointer rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-wb-amber-500"
            aria-label={isBn ? 'ইনপুট মুছুন' : 'Clear input'}
          >
            <XCircle className="w-4 h-4" aria-hidden="true" />
          </button>
        )}

        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="min-h-[44px] min-w-[44px] px-3.5 rounded-xl bg-wb-amber-700 hover:bg-wb-ochre-800 disabled:bg-slate-200 text-white disabled:text-slate-400 flex items-center justify-center transition-all cursor-pointer disabled:cursor-not-allowed shrink-0 shadow-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-wb-amber-500"
          aria-label={isBn ? 'বার্তা পাঠান' : 'Send inquiry'}
        >
          <Send className="w-4 h-4" aria-hidden="true" />
        </button>
      </div>

      {/* Footer Strip: Non-diagnostic disclaimer & Character Counter */}
      <div className="px-3 pt-1 pb-1.5 flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-500 border-t border-slate-100">
        <span>
          {isBn
            ? 'আইবুপ্রোফেন/অ্যাসপিরিন এড়িয়ে চলুন • জরুরি প্রয়োজনে ১০৮ নম্বরে যোগাযোগ করুন'
            : 'Avoid NSAIDs (Ibuprofen/Aspirin) • For medical emergencies call 108'}
        </span>
        <div className="flex items-center gap-3">
          <span className="font-mono text-slate-400">
            {input.length}/{MAX_CHARS}
          </span>
          <span className="hidden sm:inline font-mono text-slate-400">
            {isBn ? 'সরাসরি চিকিৎসা পরামর্শ নয়' : 'Health Education Only'}
          </span>
        </div>
      </div>
    </form>
  )
}
