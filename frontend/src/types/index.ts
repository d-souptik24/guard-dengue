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
  matched_rules: string[]      // Deterministic safety rules that fired
  verification_score: number   // NLI claim verification score [0, 1]
  attempts: number             // Number of draft-revision cycles (max 2)
  final_output: string
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

/** Individual SSE event streamed from /stream endpoint */
export interface StreamEvent {
  type: 'route' | 'evidence' | 'draft' | 'verdict' | 'final' | 'error'
  node: string              // LangGraph node name: screener | retriever | draft | verifier
  payload: Partial<GuardDengueResponse> | { message: string }
  timestamp: string
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
