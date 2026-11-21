/**
 * Inspector Components — index
 *
 * Dr. Wazib's Clinical Trace Panel (toggled by Inspector Mode):
 *   - InspectorPanel     → slide-in right panel containing the full trace
 *   - LangGraphTrace     → animated node-by-node state machine visualization
 *   - ClaimList          → extracted NLI claims with pass/fail verdicts
 *   - KGTriplesView      → Neo4j knowledge graph triples that fired
 *   - MetricsBar         → verification score, latency, attempt count
 *
 * This panel is the academic differentiator for the project viva.
 *
 * TODO: Implement in Session 3 frontend sprint.
 */

export { default as InspectorPanel }  from './InspectorPanel'
export { default as LangGraphTrace }  from './LangGraphTrace'
export { default as ClaimList }       from './ClaimList'
export { default as KGTriplesView }   from './KGTriplesView'
export { default as MetricsBar }      from './MetricsBar'
