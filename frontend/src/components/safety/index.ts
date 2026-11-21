/**
 * Safety Components — index
 *
 * Zone 2 deterministic safety UI components:
 *   - EmergencyBanner   → re-exported from EmergencyRibbon for backwards compatibility
 *   - MedicationWarning → amber warning dialog for NSAID contraindication
 *   - SafeAbstainCard   → neutral card shown when GuardDengue cannot answer
 */

export { default as EmergencyBanner }   from '@/components/citizen/EmergencyRibbon'
export { default as EmergencyRibbon }   from '@/components/citizen/EmergencyRibbon'
export { default as EmergencyDialog }   from './EmergencyDialog'
export { default as MedicationWarning } from './MedicationWarning'
export { default as SafeAbstainCard }   from './SafeAbstainCard'
