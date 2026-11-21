/**
 * GuardDengue — Shared TypeScript Type Definitions
 *
 * These types model the LangGraph state schema from architecture_design.md,
 * the 4-field evidence metadata contract from Plan Version 2, and the
 * 5-zone response structure defined in GuardDengue-Architecture-Review.md.
 */

// ─── LangGraph Route States (mirrors Python State TypedDict) ─────────────────

/** Maps to route: Literal["urgent", "education", "medication", "uncertain"] */
export type RouteType = 'urgent' | 'education' | 'medication' | 'uncertain'

/** Maps to verdict: Literal["pass", "revise", "reject", "template_bypass"] */
export type VerdictType = 'pass' | 'revise' | 'reject' | 'template_bypass'

// ─── Evidence Metadata Contract (Plan Version 2, §Evidence Contract) ─────────

/** Evidence levels matching the 13-category knowledge base taxonomy */
export type EvidenceLevel =
  | 'Level 1 (Global Clinical Practice Guideline)'
  | 'Level 2 (National Public Health Protocol)'
  | 'Level 2 (National Clinical Laboratory Protocol)'
  | 'Level 2 (Specialist Consensus Guideline)'
  | 'Level 3 (Public Health Operational Standard)'

/** 13 controlled topic labels from the GuardDengue knowledge taxonomy */
export type KnowledgeTopic =
  | 'Dengue basics'
  | 'Transmission'
  | 'Symptoms'
  | 'Prevention'
  | 'Hydration'
  | 'Warning signs'
  | 'Diagnosis'
  | 'Myths'
  | 'Children'
  | 'Pregnancy'
  | 'Medication safety'
  | 'Outbreak awareness'
  | 'Emergency guidance'

/** Required metadata attached to every retrieved knowledge chunk */
export interface EvidenceMetadata {
  source: string               // Canonical publisher (WHO, NCVBDC, ICMR, IAP, FOGSI)
  publication_date: string     // ISO 8601 format: YYYY-MM-DD
  evidence_level: EvidenceLevel
  topic: KnowledgeTopic | KnowledgeTopic[]
  chunk_id?: string
  review_status?: 'approved' | 'pending' | 'quarantined'
  corpus_release?: string
}

/** A retrieved evidence chunk from Qdrant */
export interface EvidenceChunk {
  id: string
  score: number                // Cosine similarity / RRF fusion score
  category: KnowledgeTopic
  content: string
  metadata: EvidenceMetadata
}

// ─── API Response Shape (from FastAPI /api/chat endpoint) ────────────────────

/** The full response payload from a completed GuardDengue pipeline run */
export interface GuardDengueResponse {
  session_id: string
  route: RouteType
  verdict: VerdictType
  answer: string               // The final published (verified) response
  evidence: EvidenceChunk[]    // Retrieved and used evidence chunks
  evidence_ok?: boolean
  attempts: number             // Number of draft-revision cycles (max 2)
  is_fallback?: boolean
  safety_disclaimer?: string   // Statutory medical disclaimer
  telephony_action?: {
    recommended_call: string
    helpline: string
  }
  matched_rules?: string[]      // Deterministic safety rules that fired
  verification_score?: number   // NLI claim verification score [0, 1]
  final_output?: string
  metrics?: {
    total_latency_ms: number
    zone2_screener_ms: number
    model_generation_ms: number
    nli_verification_ms: number
  }
  // Inspector mode fields (for clinical trace panel)
  extracted_claims?: string[]
  kg_triples?: KGTriple[]
}

/** A Neo4j knowledge graph triple */
export interface KGTriple {
  subject: string
  relation: string
  object: string
  source_chunk_id: string
  review_status: 'approved'
}

// ─── SSE Streaming Events (LangGraph state updates) ──────────────────────────

/** 8 Canonical LangGraph lifecycle events from api_contract.md §4 + legacy fallback types */
export type SSEEventType =
  | 'screener_triage'
  | 'template_bypass'
  | 'retrieval_complete'
  | 'revision_triggered'
  | 'verification_audit'
  | 'answer_publish'
  | 'answer_abstain'
  | 'stream_error'
  | 'route'
  | 'evidence'
  | 'draft'
  | 'verdict'
  | 'final'
  | 'error'

/** Individual SSE event streamed from POST /api/chat/stream endpoint */
export interface StreamEvent {
  event?: SSEEventType
  type?: SSEEventType
  node?: string              // LangGraph node name: screener | retriever | draft | verifier
  data?: any
  payload?: Partial<GuardDengueResponse> | { message: string } | any
  timestamp?: string
}

// ─── UI State Types ───────────────────────────────────────────────────────────

/** Supported UI languages */
export type AppLanguage = 'en' | 'bn'

/** Font size preference — scales html { font-size } via DOM sync */
export type FontSize = 'sm' | 'md' | 'lg'

/** High-contrast mode — sets data-contrast="high" on <html> */
export type ContrastMode = 'normal' | 'high'

/** Application-level UI settings */
export interface AppSettings {
  language: AppLanguage
  inspectorMode: boolean      // Dr. Wazib's clinical trace panel toggle
  fontSize: FontSize          // A-=sm(14px) | A=md(16px) | A+=lg(18px)
  contrast: ContrastMode      // normal | high (WCAG AA high-contrast mode)
}

/** A single chat turn */
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  language: AppLanguage
  timestamp: string
  response?: GuardDengueResponse    // Only on assistant messages
  isStreaming?: boolean
}
