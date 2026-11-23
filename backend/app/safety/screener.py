"""
GuardDengue — Clinical Triage & Red-Flag Screener (Zone 2)

Performs deterministic sub-20ms screening of citizen input.
Matches severe warning signs (urgent bypass with 108 telephony action),
contraindicated NSAIDs (medication bypass), and general dengue intent.
"""
import re
import time
from typing import Literal
from pydantic import BaseModel, Field

from app.safety.drug_registry import detect_nsaid
from app.safety.templates import (
    DISCLAIMER_BN,
    DISCLAIMER_EN,
    EMERGENCY_RED_FLAG_BN,
    EMERGENCY_RED_FLAG_EN,
    NSAID_CHRONIC_RX_BN,
    NSAID_CHRONIC_RX_EN,
    NSAID_CONTRAINDICATION_BN,
    NSAID_CONTRAINDICATION_EN,
)

# ─── Clinical Red Flag Regex Patterns ─────────────────────────────────────────
RED_FLAG_PATTERNS = [
    # Severe abdominal pain / tenderness
    (re.compile(r"\b(severe|terrible|unbearable|intense|acute)\s+.*?\b(abdominal|stomach|belly|abdomen)\s*(pain|ache|tenderness)\b", re.IGNORECASE), "Severe abdominal pain"),
    (re.compile(r"\b(abdominal|stomach|belly|abdomen)\s*(pain|ache|tenderness)\b", re.IGNORECASE), "Abdominal pain/tenderness"),
    (re.compile(r"(তীব্র|অসহ্য|মারাত্মক|প্রচণ্ড)\s*.*?(পেটে\s*ব্যথা|পেট\s*বেদনা)", re.IGNORECASE), "Severe abdominal pain (Bengali)"),
    
    # Persistent vomiting
    (re.compile(r"\b(severe|persistent|continuous|repeated|frequent|constant)\s+vomit(ing)?\b", re.IGNORECASE), "Persistent vomiting"),
    (re.compile(r"\bvomit(ed|ing)?\s+(more than|at least|>)\s*3\s*(times|episodes)\b", re.IGNORECASE), "Persistent vomiting (frequency)"),
    (re.compile(r"(অবিরাম|ঘন\s*ঘন|বার\s*বার|একটানা)\s*(বমি)", re.IGNORECASE), "Persistent vomiting (Bengali)"),
    
    # Mucosal and internal bleeding
    (re.compile(r"\b(bleeding|blood)\s+(from\s+)?(gum|gums|nose|mouth|teeth)\b", re.IGNORECASE), "Mucosal bleeding (gums/nose)"),
    (re.compile(r"\b(nosebleed|epistaxis|hematemesis|melena)\b", re.IGNORECASE), "Clinical hemorrhage sign"),
    (re.compile(r"\b(black|dark|tarry)\s+(stool|stools|potty|poop)\b", re.IGNORECASE), "Gastrointestinal bleeding (melena)"),
    (re.compile(r"\b(blood|red)\s+in\s+(vomit|stool|urine|cough)\b", re.IGNORECASE), "Internal bleeding"),
    (re.compile(r"(মাড়ি|নাক|দাঁত)\s*থেকে\s*রক্ত", re.IGNORECASE), "Mucosal bleeding (Bengali)"),
    (re.compile(r"(বমিতে|পায়খানায়|প্রস্রাবে)\s*রক্ত|(কালো\s*পায়খানা)", re.IGNORECASE), "Internal bleeding (Bengali)"),
    
    # Fluid accumulation and respiratory distress
    (re.compile(r"\b(difficulty|trouble|shortness|hard)\s*(to|in|of)?\s*(breath|breathing|breathlessness)\b", re.IGNORECASE), "Respiratory distress"),
    (re.compile(r"\b(swollen|swelling)\s+(belly|abdomen|stomach|eyelids|feet)\b", re.IGNORECASE), "Clinical fluid accumulation"),
    (re.compile(r"(শ্বাসকষ্ট|দম\s*নিতে\s*কষ্ট|পেট\s*ফোলা)", re.IGNORECASE), "Respiratory / fluid sign (Bengali)"),
    
    # Lethargy, restlessness, shock, altered consciousness
    (re.compile(r"\b(extreme|severe|total)\s+(lethargy|weakness|exhaustion|drowsiness|fatigue)\b", re.IGNORECASE), "Severe lethargy"),
    (re.compile(r"\b(unable|cannot|hard)\s+to\s+(wake|wake\s*up|stand|move|respond)\b", re.IGNORECASE), "Altered consciousness"),
    (re.compile(r"\b(cold|clammy|sweaty)\s+(hands|feet|extremities|skin)\b", re.IGNORECASE), "Hypovolemic shock warning"),
    (re.compile(r"\b(faint(ed|ing)?|collaps(ed|ing)?|unconscious)\b", re.IGNORECASE), "Syncope / Collapse"),
    (re.compile(r"(হাত\s*পা\s*ঠান্ডা|নিস্তেজ|অজ্ঞান|উদ্বেগ|জ্ঞান\s*হারানো)", re.IGNORECASE), "Shock / lethargy (Bengali)"),
    
    # Pediatric specific warnings
    (re.compile(r"\b(baby|infant|child|toddler)\s+(refusing|not|won't)\s+(drink|feed|eat|milk)\b", re.IGNORECASE), "Pediatric oral feed refusal"),
    (re.compile(r"\b(no|not|stopped)\s+urin(at|e|ing)\s+(for\s+)?(more\s+than\s+)?(6|8|12)\s*hours?\b", re.IGNORECASE), "Oliguria / kidney hypoperfusion"),
    (re.compile(r"(বাচ্চা|শিশু)\s*(দুধ\s*খাচ্ছে\s*না|প্রস্রাব\s*করছে\s*না|নিস্তেজ)", re.IGNORECASE), "Pediatric warning (Bengali)"),
]

# ─── Dengue Domain Relevance Filter ──────────────────────────────────────────
DENGUE_DOMAIN_KEYWORDS = [
    "dengue", "dangee", "denv", "fever", "feverish", "high temp", "temperature",
    "platelet", "platelets", "thrombocytopenia", "ns1", "igm", "igg", "cbc", "hematocrit",
    "mosquito", "aedes", "larvae", "bite", "stagnant",
    "paracetamol", "calpol", "crocin", "dolo", "brufen", "aspirin", "combiflam",
    "fluid", "hydration", "ors", "coconut water", "papaya", "kiwi",
    "rash", "headache", "retro-orbital", "eye pain", "joint pain", "breakbone",
    "critical phase", "defervescence", "plasma leakage", "transfusion",
    "ডেঙ্গু", "জ্বর", "প্লাটিলেট", "মশা", "এডিস", "প্যারাসিটামল", "ওআরএস", "রক্তপরীক্ষা"
]

class TriageDecision(BaseModel):
    route: Literal["urgent", "medication", "education", "uncertain"]
    matched_rules: list[str] = Field(default_factory=list)
    intent_description: str
    direct_template: str | None = None
    dial_108: bool = False
    telephony_action: dict[str, str] | None = None
    safety_disclaimer: str
    zone2_latency_ms: float = 0.0

def screen_query(query: str, language: Literal["en", "bn"] = "en") -> TriageDecision:
    """
    Executes Zone 2 deterministic screening against incoming citizen text.
    Latency is guaranteed sub-20ms.
    """
    start_time = time.perf_counter()
    matched_rules: list[str] = []
    disclaimer = DISCLAIMER_BN if language == "bn" else DISCLAIMER_EN
    
    # ── Step 1: Emergency Red Flag Screening ──────────────────────────────────
    red_flag_triggers = []
    for pattern, label in RED_FLAG_PATTERNS:
        if pattern.search(query):
            red_flag_triggers.append(label)
            
    if red_flag_triggers:
        latency = (time.perf_counter() - start_time) * 1000.0
        template = EMERGENCY_RED_FLAG_BN if language == "bn" else EMERGENCY_RED_FLAG_EN
        return TriageDecision(
            route="urgent",
            matched_rules=["EMERGENCY_RED_FLAG"] + [f"RED_FLAG:{r}" for r in red_flag_triggers],
            intent_description=f"Clinical Emergency Warning Sign detected: {', '.join(red_flag_triggers)}",
            direct_template=template,
            dial_108=True,
            telephony_action={
                "type": "tel_prompt",
                "number": "108",
                "label": "Call 108 Emergency Ambulance" if language == "en" else "১০৮ এম্বুলেন্সে কল করুন"
            },
            safety_disclaimer=disclaimer,
            zone2_latency_ms=round(latency, 2)
        )
        
    # ── Step 2: Medication & NSAID Screening ─────────────────────────────────
    nsaid_match = detect_nsaid(query)
    if nsaid_match:
        latency = (time.perf_counter() - start_time) * 1000.0
        drug_name = nsaid_match["matched_term"].title()
        generic_name = nsaid_match["generic_name"]
        is_chronic = nsaid_match["is_chronic_context"]
        
        if language == "bn":
            base_template = NSAID_CONTRAINDICATION_BN.format(drug_name=drug_name)
            if is_chronic:
                base_template += "\n\n" + NSAID_CHRONIC_RX_BN.format(drug_name=drug_name)
        else:
            base_template = NSAID_CONTRAINDICATION_EN.format(drug_name=drug_name)
            if is_chronic:
                base_template += "\n\n" + NSAID_CHRONIC_RX_EN.format(drug_name=drug_name)
                
        rules = [f"NSAID_CONTRAINDICATION:{generic_name}"]
        if is_chronic:
            rules.append("CHRONIC_PRESCRIPTION_CAVEAT")
            
        return TriageDecision(
            route="medication",
            matched_rules=rules,
            intent_description=f"Contraindicated medication inquired: {generic_name} ({drug_name})",
            direct_template=base_template,
            dial_108=False,
            telephony_action=None,
            safety_disclaimer=disclaimer,
            zone2_latency_ms=round(latency, 2)
        )
        
    # ── Step 3: Domain Relevance Check ───────────────────────────────────────
    query_lower = query.lower()
    is_dengue_related = any(kw in query_lower for kw in DENGUE_DOMAIN_KEYWORDS)
    
    latency = (time.perf_counter() - start_time) * 1000.0
    
    if is_dengue_related:
        return TriageDecision(
            route="education",
            matched_rules=["DENGUE_CLINICAL_EDUCATION"],
            intent_description="Dengue clinical or management query requiring evidence retrieval",
            direct_template=None,
            dial_108=False,
            telephony_action=None,
            safety_disclaimer=disclaimer,
            zone2_latency_ms=round(latency, 2)
        )
    else:
        # Out-of-scope query
        return TriageDecision(
            route="uncertain",
            matched_rules=["OUT_OF_SCOPE_QUERY"],
            intent_description="Non-dengue or out-of-scope health inquiry",
            direct_template=None,
            dial_108=False,
            telephony_action=None,
            safety_disclaimer=disclaimer,
            zone2_latency_ms=round(latency, 2)
        )
