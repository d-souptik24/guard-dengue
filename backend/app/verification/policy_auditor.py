"""
GuardDengue — Policy & Safety Auditor (Zone 5)

Performs deterministic post-generation safety verification.
Ensures that no generative hallucinations recommend contraindicated NSAIDs,
unsupported medications, or dangerous fluid management procedures.
"""
import re
from app.retrieval.policy_store import policy_store

# Prohibited action patterns in dengue clinical drafts
PROHIBITED_PHRASES = [
    re.compile(r"\b(take|administer|consume|prescribe|use)\s+(aspirin|disprin|ibuprofen|brufen|combiflam|diclofenac|voveran)\b", re.IGNORECASE),
    re.compile(r"\b(aspirin|ibuprofen|combiflam|diclofenac)\s+(is|are)\s+(safe|recommended|effective)\b", re.IGNORECASE),
    re.compile(r"\b(transfuse|infuse)\s+platelets\s+immediately\s+without\b", re.IGNORECASE),
]

def audit_draft_against_policies(draft_text: str) -> tuple[bool, list[str]]:
    """
    Audits the generated draft against clinical policies.
    Returns:
        is_safe: False if any hard policy rule was violated
        violations: List of specific clinical violation descriptions
    """
    violations = []
    
    # 1. Check prohibited phrasing
    for pattern in PROHIBITED_PHRASES:
        match = pattern.search(draft_text)
        if match:
            violations.append(f"Prohibited medication recommendation detected: '{match.group(0)}'")

    # 2. Check if any contraindicated drug was affirmatively suggested
    # Note: Mentions warning AGAINST them are permitted (e.g. "Do not take Ibuprofen")
    # We flag only if the text suggests taking them without negative framing.
    lines = draft_text.splitlines()
    for line in lines:
        line_lower = line.lower()
        if any(kw in line_lower for kw in ["do not", "avoid", "contraindicated", "never", "prohibited", "harmful"]):
            continue  # Safe negative mention
        for rule in policy_store.get_rules_for_condition("dengue"):
            for drug in rule.get("drug_members", []):
                name = drug["name"].lower()
                if f" {name} " in f" {line_lower} " or f" {drug['id']} " in f" {line_lower} ":
                    violations.append(f"Unguarded mention of contraindicated drug '{drug['name']}' in line: '{line.strip()}'")

    return (len(violations) == 0), violations
