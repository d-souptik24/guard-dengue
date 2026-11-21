/**
 * Safety Components — index
 *
 * Zone 2 deterministic safety UI components:
 *   - EmergencyBanner   → full-width crimson alert for urgent/red-flag queries
 *   - MedicationWarning → amber warning dialog for NSAID contraindication
 *   - SafeAbstainCard   → neutral card shown when GuardDengue cannot answer
 *
 * These components receive pre-routed responses (route = "urgent" | "medication" | "uncertain")
 * and render deterministic templates, NOT generative model output.
 *
 * TODO: Implement in Session 3 frontend sprint.
 */

export { default as EmergencyBanner }   from './EmergencyBanner'
export { default as MedicationWarning } from './MedicationWarning'
export { default as SafeAbstainCard }   from './SafeAbstainCard'
