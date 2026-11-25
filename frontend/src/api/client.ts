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

// ─── SSE Streaming Chat (POST /api/chat/stream with fetch & ReadableStream) ────

export function streamMessage(
  req: ChatRequest,
  onEvent: (event: StreamEvent) => void,
  onError: (error: Error) => void,
  onDone: () => void,
): () => void {
  const controller = new AbortController()

  async function startStream() {
    try {
      const res = await fetch(ENDPOINTS.stream, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify(req),
        signal: controller.signal,
      })

      if (!res.ok) {
        throw new Error(`SSE stream error: ${res.status} ${res.statusText}`)
      }

      if (!res.body) {
        throw new Error('Response body is null')
      }

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const blocks = buffer.split('\n\n')
        buffer = blocks.pop() || ''

        for (const block of blocks) {
          if (!block.trim()) continue
          let eventType = ''
          let eventData = ''

          for (const line of block.split('\n')) {
            if (line.startsWith('event:')) {
              eventType = line.slice(6).trim()
            } else if (line.startsWith('data:')) {
              eventData = line.slice(5).trim()
            }
          }

          if (eventData) {
            try {
              const parsedData = JSON.parse(eventData)
              const streamEvt: StreamEvent = {
                event: (eventType as any) || parsedData.event,
                type: (eventType as any) || parsedData.type,
                data: parsedData.data || parsedData,
                payload: parsedData.payload || parsedData,
                node: parsedData.node,
                timestamp: parsedData.timestamp || new Date().toISOString(),
              }
              onEvent(streamEvt)
              if (
                eventType === 'answer_publish' ||
                eventType === 'answer_abstain' ||
                parsedData.type === 'final'
              ) {
                onDone()
                return
              }
            } catch {
              // Skip non-JSON SSE heartbeat/ping lines
            }
          }
        }
      }
      onDone()
    } catch (err: any) {
      if (err.name !== 'AbortError') {
        onError(err instanceof Error ? err : new Error(String(err)))
      }
    }
  }

  startStream()

  return () => controller.abort()
}

// ─── Health Check ─────────────────────────────────────────────────────────────

export async function healthCheck(): Promise<{ status: string }> {
  const res = await fetch(ENDPOINTS.health)
  return res.json() as Promise<{ status: string }>
}
