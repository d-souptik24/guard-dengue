/**
 * Chat Components — index
 *
 *   - ChatWindow        → scrollable conversation container
 *   - MessageBubble     → individual user/assistant turn with route badges
 *   - ChatInput         → bilingual text input with voice-to-text hook (future)
 *   - QuickPrompts      → suggestion pill buttons for common dengue queries
 *   - TypingIndicator   → animated "Analyzing..." state during pipeline run
 *
 * TODO: Implement in Session 3 frontend sprint.
 */

export { default as ChatWindow }      from './ChatWindow'
export { default as MessageBubble }   from './MessageBubble'
export { default as ChatInput }       from './ChatInput'
export { default as QuickPrompts }    from './QuickPrompts'
export { default as TypingIndicator } from './TypingIndicator'
