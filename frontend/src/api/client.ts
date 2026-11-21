/**
 * GuardDengue — API Client
 *
 * Handles all communication with the FastAPI + LangGraph backend.
 * Supports both one-shot JSON responses and SSE streaming for real-time
 * LangGraph state-node updates (used by the Inspector Mode panel).
 */
import type { GuardDengueResponse, StreamEvent } from '@/types'
import { ENDPOINTS } from '@/constants'

// ─── One-Shot Chat Request ────────────────────────────────────────────────────

export interface ChatRequest {
  message: string
  session_id?: string
  language?: 'en' | 'bn'
}

export async function sendMessage(req: ChatRequest): Promise<GuardDengueResponse> {
  const res = await fetch(ENDPOINTS.chat, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(`GuardDengue API error: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<GuardDengueResponse>
}

// ─── SSE Streaming Chat (for Inspector Mode) ──────────────────────────────────

export function streamMessage(
  req: ChatRequest,
  onEvent: (event: StreamEvent) => void,
  onError: (error: Error) => void,
  onDone: () => void,
): () => void {
  const url = new URL(ENDPOINTS.stream, window.location.origin)
  url.searchParams.set('message', req.message)
  if (req.session_id) url.searchParams.set('session_id', req.session_id)
  if (req.language)   url.searchParams.set('language', req.language)

  const es = new EventSource(url.toString())

  es.addEventListener('message', (e) => {
    try {
      const parsed = JSON.parse(e.data) as StreamEvent
      onEvent(parsed)
      if (parsed.type === 'final') {
        es.close()
        onDone()
      }
    } catch {
      onError(new Error('Failed to parse SSE event'))
      es.close()
    }
  })

  es.addEventListener('error', () => {
    onError(new Error('SSE connection error'))
    es.close()
  })

  // Return cleanup function
  return () => es.close()
}

// ─── Health Check ─────────────────────────────────────────────────────────────

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(ENDPOINTS.health)
  return res.json() as Promise<{ status: string }>
}
