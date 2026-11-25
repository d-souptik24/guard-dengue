"""
GuardDengue — Claim Verification Engine (Zone 5)

Unified Claim Verification Gate coordinating claim extraction, policy audit,
and NLI evidence alignment to issue a certified clinical verdict.
Verdicts:
  - 'pass': Clinically sound, entailed by guidelines, zero policy violations
  - 'revise': Moderate score or unsupported non-critical claims; triggers bounded loop (max 2)
  - 'reject': Hard safety violation (e.g. NSAID recommendation); triggers immediate fallback
"""
import time
from typing import Any, Literal
from pydantic import BaseModel, Field

from app.verification.claim_extractor import extract_claims
from app.verification.policy_auditor import audit_draft_against_policies
from app.verification.nli_auditor import audit_claims_nli

VerdictType = Literal["pass", "revise", "reject", "template_bypass"]

class VerificationReport(BaseModel):
    verdict: VerdictType
    verification_score: float
    conflict_counts: dict[str, int]
    extracted_claims: list[str]
    violations: list[str] = Field(default_factory=list)
    claim_details: list[dict[str, Any]] = Field(default_factory=list)
    verification_latency_ms: float = 0.0

class VerificationEngine:
    def verify(
        self,
        draft_text: str,
        evidence_chunks: list[dict[str, Any]],
        user_question: str
    ) -> VerificationReport:
        start_time = time.perf_counter()
        
        # 1. Deterministic Policy Audit (Failsafe)
        is_safe, violations = audit_draft_against_policies(draft_text)
        if not is_safe:
            latency = (time.perf_counter() - start_time) * 1000.0
            return VerificationReport(
                verdict="reject",
                verification_score=0.0,
                conflict_counts={"input_conflicts": 0, "context_conflicts": 0, "fact_conflicts": len(violations)},
                extracted_claims=[],
                violations=violations,
                claim_details=[],
                verification_latency_ms=round(latency, 2)
            )

        # 2. Extract atomic claims
        claims = extract_claims(draft_text)

        # 3. NLI Audit against evidence
        score, conflicts, details = audit_claims_nli(claims, evidence_chunks, user_question)

        # 4. Determine Verdict
        if score >= 0.75 and conflicts["context_conflicts"] == 0:
            verdict: VerdictType = "pass"
        elif score >= 0.60:
            verdict = "revise"
        else:
            verdict = "reject"

        latency = (time.perf_counter() - start_time) * 1000.0
        return VerificationReport(
            verdict=verdict,
            verification_score=score,
            conflict_counts=conflicts,
            extracted_claims=claims,
            violations=[],
            claim_details=details,
            verification_latency_ms=round(latency, 2)
        )

# Singleton instance
verification_engine = VerificationEngine()
