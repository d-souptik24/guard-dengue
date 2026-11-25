"""
GuardDengue — Claim Extractor (Zone 5)

Deconstructs a candidate model draft into atomic clinical propositions/claims
for fine-grained NLI entailment verification.
"""
import re

def extract_claims(text: str) -> list[str]:
    """
    Extracts atomic clinical propositions from drafted markdown or prose.
    Splits by bullet points, sentences, and numbered lists.
    """
    clean_text = re.sub(r"[*#_`]", "", text)
    lines = clean_text.splitlines()
    raw_claims = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Split line by sentence terminators if multiple sentences exist
        sentences = re.split(r"(?<=[.!?])\s+", line)
        for s in sentences:
            s = s.strip()
            # Filter out generic headers or tiny fragments
            if len(s) > 15 and not s.endswith(":"):
                raw_claims.append(s)
                
    return raw_claims if raw_claims else [clean_text.strip()]
