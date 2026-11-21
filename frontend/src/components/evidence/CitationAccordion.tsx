/**
 * CitationAccordion — WHO & ICMR Provenance & Citation Viewer
 *
 * Built on @radix-ui/react-accordion for accessible, collapsible inspection
 * of the 4-field clinical evidence metadata contract:
 *   1. source (WHO, ICMR, National Protocols)
 *   2. publication_date (ISO 8601)
 *   3. evidence_level (Level 1, Level 2, Level 3)
 *   4. topic (Taxonomy chips)
 */
import * as Accordion from '@radix-ui/react-accordion'
import type { EvidenceChunk } from '@/types'
import { ChevronDown, BookOpen, Calendar, Tag, FileText } from 'lucide-react'
import EvidenceBadge from './EvidenceBadge'
import { useSettings } from '@/store/settings'

export interface CitationAccordionProps {
  evidence: EvidenceChunk[]
  className?: string
}

export default function CitationAccordion({ evidence, className = '' }: CitationAccordionProps) {
  const { settings } = useSettings()
  const isBn = settings.language === 'bn'

  if (!evidence || evidence.length === 0) return null

  return (
    <div className={`mt-3 pt-3 border-t border-slate-200/80 ${className}`}>
      <div className="flex items-center gap-1.5 mb-2 text-xs font-semibold text-slate-700">
        <BookOpen className="w-3.5 h-3.5 text-wb-teal-evidence" aria-hidden="true" />
        <span>
          {isBn
            ? `ক্লিনিক্যাল প্রমাণের উৎস (${evidence.length}টি নির্দেশিকা)`
            : `Clinical Citations & Provenance (${evidence.length})`}
        </span>
      </div>

      <Accordion.Root type="single" collapsible className="w-full space-y-2">
        {evidence.map((chunk, idx) => {
          const meta = chunk.metadata
          const itemKey = chunk.id || `cit-${idx}`

          return (
            <Accordion.Item
              key={itemKey}
              value={itemKey}
              className="border border-slate-200 rounded-xl overflow-hidden bg-slate-50/60 transition-colors"
            >
              <Accordion.Header className="flex">
                <Accordion.Trigger className="w-full min-h-[44px] px-3.5 py-2 flex items-center justify-between text-left text-xs font-medium text-slate-800 hover:bg-slate-100/80 transition-all cursor-pointer group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-wb-amber-500">
                  <div className="flex items-center gap-2 overflow-hidden pr-2">
                    <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 text-[10px] font-bold flex items-center justify-center shrink-0">
                      {idx + 1}
                    </span>
                    <span className="truncate font-semibold text-slate-900">
                      {meta?.source || 'Authorized Guideline'}
                    </span>
                    {meta?.evidence_level && (
                      <span className="hidden sm:inline">
                        <EvidenceBadge level={meta.evidence_level} />
                      </span>
                    )}
                  </div>
                  <ChevronDown
                    className="w-4 h-4 text-slate-500 shrink-0 transition-transform duration-200 group-data-[state=open]:rotate-180"
                    aria-hidden="true"
                  />
                </Accordion.Trigger>
              </Accordion.Header>

              <Accordion.Content className="px-3.5 pt-1 pb-3 text-xs text-slate-600 space-y-2 border-t border-slate-200/60 bg-white data-[state=open]:animate-in data-[state=closed]:animate-out duration-200">
                {/* Excerpt */}
                {chunk.content && (
                  <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80 text-[11px] text-slate-700 leading-relaxed font-sans">
                    <FileText className="w-3 h-3 text-slate-400 inline mr-1 -mt-0.5" aria-hidden="true" />
                    {chunk.content}
                  </div>
                )}

                {/* Metadata Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1">
                  {meta?.publication_date && (
                    <div className="flex items-center gap-1.5 text-slate-500">
                      <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" aria-hidden="true" />
                      <span>{isBn ? 'প্রকাশকাল: ' : 'Published: '}</span>
                      <strong className="text-slate-700">{meta.publication_date}</strong>
                    </div>
                  )}

                  {meta?.chunk_id && (
                    <div className="flex items-center gap-1.5 text-slate-500">
                      <Tag className="w-3.5 h-3.5 text-slate-400 shrink-0" aria-hidden="true" />
                      <span>Chunk ID: </span>
                      <code className="px-1 py-0.5 rounded bg-slate-100 font-mono text-[10px] text-slate-800">
                        {meta.chunk_id}
                      </code>
                    </div>
                  )}
                </div>

                {/* Topics */}
                {(() => {
                  const topics = Array.isArray(meta?.topic)
                    ? meta.topic
                    : meta?.topic
                    ? [meta.topic]
                    : []
                  if (topics.length === 0) return null
                  return (
                    <div className="flex flex-wrap items-center gap-1.5 pt-1">
                      <span className="text-[10px] text-slate-500">{isBn ? 'বিষয়শ্রেণী:' : 'Topics:'}</span>
                      {topics.map((t, tIdx) => (
                        <span
                          key={tIdx}
                          className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 text-[10px] font-medium"
                        >
                          {String(t)}
                        </span>
                      ))}
                    </div>
                  )
                })()}
              </Accordion.Content>
            </Accordion.Item>
          )
        })}
      </Accordion.Root>
    </div>
  )
}
