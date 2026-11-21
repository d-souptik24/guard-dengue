/**
 * Hooks — index
 *
 *   - useChat       → manages chat history, sends messages, handles SSE stream
 *   - useStream     → raw SSE stream hook (used by useChat + InspectorPanel)
 *   - useLanguage   → shortcut to settings language with TOPIC_LABELS lookup
 *
 * TODO: Implement in Session 3 frontend sprint.
 */

export { useChat }     from './useChat'
export { useStream }   from './useStream'
export { useLanguage } from './useLanguage'
