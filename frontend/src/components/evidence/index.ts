/**
 * Evidence Components — index
 *
 *   - EvidenceBadge      → inline chip: topic label + evidence level
 *   - CitationCard       → expandable accordion showing full chunk + source
 *   - EvidenceDrawer     → slide-in panel listing all retrieved evidence chunks
 *   - VerificationBadge  → shows verification score + verdict (pass/revise/reject)
 *
 * These implement the citation transparency required by Plan Version 2's
 * 4-field evidence metadata contract.
 *
 * TODO: Implement in Session 3 frontend sprint.
 */

export { default as EvidenceBadge }     from './EvidenceBadge'
export { default as CitationCard }      from './CitationCard'
export { default as EvidenceDrawer }    from './EvidenceDrawer'
export { default as VerificationBadge } from './VerificationBadge'
