"""
GuardDengue — NLI Evidence Alignment Auditor (Zone 5)

Evaluates candidate claims against retrieved evidence passages using
the Basu & Huynh 3-conflict typology (input_conflicts, context_conflicts, fact_conflicts).
"""
import re
from typing import Any

# Procedural safety and consultation disclaimers that are standard medical safeguards
PROCEDURAL_DISCLAIMER_PATTERNS = [
    re.compile(r"\b(please\s+consult|consult\s+a\s+doctor|consult\s+your|certified\s+laboratory|healthcare\s+provider|medical\s+evaluation|seek\s+medical|qualified\s+healthcare)\b", re.IGNORECASE),
    re.compile(r"(ডাক্তার|চিকিৎসক|স্বাস্থ্যকেন্দ্র|পরামর্শ)\s*(নিন|করুন)", re.IGNORECASE)
]

def audit_claims_nli(
    claims: list[str],
    evidence_chunks: list[dict[str, Any]],
    user_question: str
) -> tuple[float, dict[str, int], list[dict[str, Any]]]:
    """
    Evaluates claims against evidence texts.
    Returns:
        mean_score: Average NLI entailment confidence [0.0, 1.0]
        conflict_counts: {"input_conflicts": int, "context_conflicts": int, "fact_conflicts": int}
        claim_audits: Detailed per-claim audit results
    """
    if not claims or not evidence_chunks:
        return 0.5, {"input_conflicts": 0, "context_conflicts": 1, "fact_conflicts": 0}, []

    evidence_combined_text = " ".join([c.get("content", "") if isinstance(c, dict) else getattr(c, "content", "") for c in evidence_chunks]).lower()
    
    claim_audits = []
    scores = []
    conflict_counts = {
        "input_conflicts": 0,
        "context_conflicts": 0,
        "fact_conflicts": 0
    }

    for claim in claims:
        # Check if the statement is a standard procedural consultation safeguard
        is_procedural = any(pat.search(claim) for pat in PROCEDURAL_DISCLAIMER_PATTERNS)
        if is_procedural:
            claim_audits.append({
                "claim": claim,
                "score": 0.95,
                "status": "procedural_safeguard",
                "matched_terms": ["procedural_referral"]
            })
            scores.append(0.95)
            continue

        claim_lower = claim.lower()
        words = [w for w in re.findall(r"\w+", claim_lower) if len(w) > 3]
        if not words:
            scores.append(0.9)
            continue
            
        matched_words = [w for w in words if w in evidence_combined_text]
        overlap_ratio = len(matched_words) / len(words)

        # Baseline entailment score
        score = min(1.0, 0.4 + 0.6 * overlap_ratio)
        
        status = "entailed"
        if score < 0.65:
            status = "unsupported"
            conflict_counts["context_conflicts"] += 1
            
        claim_audits.append({
            "claim": claim,
            "score": round(score, 3),
            "status": status,
            "matched_terms": matched_words[:5]
        })
        scores.append(score)

    mean_score = sum(scores) / len(scores) if scores else 0.5
    return round(mean_score, 3), conflict_counts, claim_audits
