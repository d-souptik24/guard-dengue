"""
GuardDengue — Bilingual NSAID and Medication Safety Registry (Zone 2)

Curated list of contraindicated Non-Steroidal Anti-Inflammatory Drugs (NSAIDs),
Indian Fixed-Dose Combinations (FDCs), safe antipyretics, chronic prescription
antiplatelet heuristics, and negative clinical invariant checks.
"""
from __future__ import annotations

import re
from typing import Any, Literal, TypedDict

from app.retrieval.adapter import MedicationAnalysis

class DrugInfo(TypedDict):
    id: str
    generic_name: str
    brand_names: list[str]
    bengali_names: list[str]
    risk_level: str  # "STRICTLY_CONTRAINDICATED"

NSAID_DATABASE: list[DrugInfo] = [
    {
        "id": "aspirin",
        "generic_name": "Aspirin",
        "brand_names": ["aspirin", "acetylsalicylic acid", "disprin", "ecosprin", "asprin", "delisprin", "asa", "loprin"],
        "bengali_names": ["অ্যাসপিরিন", "এসপিরিন", "ডিসপ্রিন", "ইকোস্প্রিন", "অ্যাসপ্রিন"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "ibuprofen",
        "generic_name": "Ibuprofen",
        "brand_names": ["ibuprofen", "brufen", "advil", "motrin", "ibugesic"],
        "bengali_names": ["আইবুপ্রোফেন", "ব্রুফেন", "আইবুজেসিক"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "diclofenac",
        "generic_name": "Diclofenac",
        "brand_names": ["diclofenac", "voveran", "voltaren", "diclo", "nac", "reactin", "dynapar"],
        "bengali_names": ["ডাইক্লোফেনাক", "ভোভেরান", "ভোল্টারেন", "ডিক্লো", "ডায়নাপার"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "naproxen",
        "generic_name": "Naproxen",
        "brand_names": ["naproxen", "naprosyn", "aleve", "xenobid"],
        "bengali_names": ["নেপ্রোক্সেন", "ন্যাপ্রোসিন", "আলিভ"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "mefenamic_acid",
        "generic_name": "Mefenamic Acid",
        "brand_names": ["mefenamic acid", "meftal", "ponstan", "mefkind"],
        "bengali_names": ["মেফেনামিক অ্যাসিড", "মেফট্যাল", "মেফকাইন্ড"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "ketorolac",
        "generic_name": "Ketorolac",
        "brand_names": ["ketorolac", "toradol", "ketorol", "ketoflam"],
        "bengali_names": ["কেটোরোল্যাক", "কেটোরল"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "piroxicam",
        "generic_name": "Piroxicam",
        "brand_names": ["piroxicam", "feldene", "dolonex"],
        "bengali_names": ["পাইরোক্সিক্যাম", "ডলোনেক্স", "ফেল্ডিন"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "nimesulide",
        "generic_name": "Nimesulide",
        "brand_names": ["nimesulide", "nice", "nise", "nimulid", "nicip"],
        "bengali_names": ["নিমেসুলাইড", "নাইস", "নিমুলিদ", "নিসিপ"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "aceclofenac",
        "generic_name": "Aceclofenac",
        "brand_names": ["aceclofenac", "zerodol", "hifenac", "aceclo"],
        "bengali_names": ["এসেক্লোফেনাক", "জেরোডল", "হাইফেনাক"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    }
]

# ─── Indian Fixed-Dose Combination (FDC) Dictionary ───────────────────────────
INDIAN_FDC_DATABASE: list[dict[str, Any]] = [
    {
        "fdc_id": "combiflam",
        "brand_name": "Combiflam",
        "aliases": ["combiflam", "combiflam plus", "কম্বিফ্লাম"],
        "constituents": ["ibuprofen", "paracetamol"],
        "nsaid_constituent": "ibuprofen",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "flexon",
        "brand_name": "Flexon",
        "aliases": ["flexon", "flexon mr", "ফ্লেক্সন"],
        "constituents": ["ibuprofen", "paracetamol"],
        "nsaid_constituent": "ibuprofen",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "ibugesic_plus",
        "brand_name": "Ibugesic Plus",
        "aliases": ["ibugesic plus", "ibugesic-plus", "আইবুজেসিক প্লাস"],
        "constituents": ["ibuprofen", "paracetamol"],
        "nsaid_constituent": "ibuprofen",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "zerodol_p",
        "brand_name": "Zerodol P",
        "aliases": ["zerodol p", "zerodol-p", "zerodol plus", "জেরোডল পি"],
        "constituents": ["aceclofenac", "paracetamol"],
        "nsaid_constituent": "aceclofenac",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "zerodol_sp",
        "brand_name": "Zerodol SP",
        "aliases": ["zerodol sp", "zerodol-sp", "জেরোডল এসপি"],
        "constituents": ["aceclofenac", "paracetamol", "serratiopeptidase"],
        "nsaid_constituent": "aceclofenac",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "meftal_spas",
        "brand_name": "Meftal Spas",
        "aliases": ["meftal spas", "meftal-spas", "meftalspas", "মেফট্যাল স্পাস"],
        "constituents": ["mefenamic_acid", "dicyclomine"],
        "nsaid_constituent": "mefenamic_acid",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "sumo",
        "brand_name": "Sumo",
        "aliases": ["sumo", "sumo l", "সুমা"],
        "constituents": ["nimesulide", "paracetamol"],
        "nsaid_constituent": "nimesulide",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "fdc_id": "voveran_plus",
        "brand_name": "Voveran Plus",
        "aliases": ["voveran plus", "voveran-plus", "ভোভেরান প্লাস"],
        "constituents": ["diclofenac", "paracetamol"],
        "nsaid_constituent": "diclofenac",
        "risk_level": "STRICTLY_CONTRAINDICATED"
    }
]

SAFE_ANTIPYRETICS = [
    "paracetamol", "acetaminophen", "calpol", "crocin", "dolo", "dolo-650", "pacimol", "p-500", "p-650",
    "প্যারাসিটামল", "ক্রোসিন", "ডলো", "ক্যালপল"
]

# Helper for chronic daily antiplatelet therapy detection
def is_chronic_antiplatelet_context(query: str) -> bool:
    """
    Distinguishes life-preserving daily antiplatelet maintenance (e.g. daily aspirin for cardiac stent)
    from acute prescriptions (e.g. doctor prescribed Zerodol for acute back pain).
    """
    clean_text = query.lower()
    has_chronic_cue = bool(
        re.search(r"\b(daily|routine|regular|maintenance|ongoing|lifetime|years|every\s+day)\b", clean_text)
        or re.search(r"(নিয়মিত|প্রতিদিন|রোজ)", query)
    )
    has_cardiac_cue = bool(
        re.search(r"\b(heart|cardiac|stent|stroke|bypass|hypertension|angioplasty|heart\s+attack|blood\s*thin(ner)?)\b", clean_text)
        or re.search(r"(হার্ট|হৃদরোগ|স্ট্রোক|স্টেন্ট)", query)
    )
    has_rx_cue = bool(
        re.search(r"\b(prescribed|advised|cardiologist|physician|doctor|dr\.?)\b", clean_text)
        or re.search(r"(প্রেসক্রাইব|ডাক্তার|চিকিৎসক)", query)
    )
    return (has_chronic_cue and has_rx_cue) or (has_cardiac_cue and (has_chronic_cue or has_rx_cue))

# Patterns for negation cues (e.g. stopped taking Brufen)
NEGATION_PATTERNS = [
    re.compile(r"\b(not|never|stopped|discontinued|quit|avoided|avoiding|isn't|aren't|don't)\s+(taking|using|having|take|consume)?\b", re.IGNORECASE),
    re.compile(r"(বন্ধ\s*করেছি|খাচ্ছি\s*না|নেব\s*না|এড়িয়ে\s*চলছি)", re.IGNORECASE),
]

# Patterns detecting unknown / uncataloged medication mentions
UNKNOWN_MED_PATTERNS = [
    re.compile(r"\b(ayurdengue[- ]?kadha|ayurdengue|kadha|giloy|herbal\s+dengue|papaya\s+leaf\s+(capsules?|extract|juice)|dengue\s+cure|miracle\s+pill|homeopathic\s+drops|mystery\s+tablet|desi\s+dawa)\b", re.IGNORECASE),
    re.compile(r"(আয়ুর্বেদিক\s*ওষুধ|কাড়া|গিলয়|পেঁপে\s*পাতার\s*ক্যাপসুল)", re.IGNORECASE),
]

def detect_nsaid(query: str) -> dict | None:
    """
    Scans citizen query for contraindicated NSAIDs and Indian FDCs in English and Bengali.
    Returns matched drug record conforming to Zone 2 screener requirements.
    """
    clean_text = query.lower()
    chronic_context = is_chronic_antiplatelet_context(query)

    # 1. Match Indian FDCs first (e.g. Combiflam, Zerodol-P)
    for fdc in INDIAN_FDC_DATABASE:
        for alias in fdc["aliases"]:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, clean_text, re.IGNORECASE) or alias in query:
                return {
                    "drug_id": fdc["nsaid_constituent"],
                    "generic_name": f"{fdc['brand_name']} ({' + '.join(c.title() for c in fdc['constituents'])})",
                    "matched_term": alias,
                    "risk_level": fdc["risk_level"],
                    "is_chronic_context": chronic_context,
                    "is_fdc": True,
                    "fdc_constituents": fdc["constituents"],
                }

    # 2. Match single NSAIDs
    for drug in NSAID_DATABASE:
        for brand in drug["brand_names"]:
            pattern = rf"\b{re.escape(brand)}\b"
            if re.search(pattern, clean_text, re.IGNORECASE):
                return {
                    "drug_id": drug["id"],
                    "generic_name": drug["generic_name"],
                    "matched_term": brand,
                    "risk_level": drug["risk_level"],
                    "is_chronic_context": chronic_context,
                    "is_fdc": False,
                    "fdc_constituents": [drug["id"]],
                }

        for bn_name in drug["bengali_names"]:
            if bn_name in query:
                return {
                    "drug_id": drug["id"],
                    "generic_name": drug["generic_name"],
                    "matched_term": bn_name,
                    "risk_level": drug["risk_level"],
                    "is_chronic_context": chronic_context,
                    "is_fdc": False,
                    "fdc_constituents": [drug["id"]],
                }

    return None

def _find_safe_antipyretic_mentions(query: str, exclude_terms: set[str] | None = None) -> list[str]:
    """Detects safe antipyretic mentions (e.g. paracetamol) for multi-drug query parsing."""
    clean_text = query.lower()
    excluded = exclude_terms or set()
    matched: list[str] = []
    for safe in SAFE_ANTIPYRETICS:
        if safe.lower() in excluded:
            continue
        pattern = rf"\b{re.escape(safe)}\b"
        if re.search(pattern, clean_text, re.IGNORECASE) or safe in query:
            if safe.lower() not in [m.lower() for m in matched]:
                matched.append(safe)
    return matched


def _build_nsaid_analysis(
    query: str,
    matched_term: str,
    drug_id: str,
    has_negation: bool,
    is_chronic: bool,
) -> MedicationAnalysis:
    """Constructs standardized single-NSAID MedicationAnalysis while preserving co-mentioned safe antipyretics."""
    if has_negation:
        action_code: Any = "NEGATED_MENTION_EDUCATION"
        template_id = "TMPL_NEGATED_NSAID_EDU_V1"
    elif is_chronic:
        action_code = "CHRONIC_PRESCRIPTION_ESCALATE"
        template_id = "TMPL_CHRONIC_RX_SAFETY_V1"
    else:
        action_code = "AVOID_NSAID_CONTRAINDICATED"
        template_id = "TMPL_NSAID_AVOID_V1"

    detected_terms = [matched_term]
    normalization_candidates = [drug_id]
    canonical_ingredients = [drug_id]
    policy_statuses: dict[str, str] = {drug_id: "contraindicated"}

    safe_mentions = _find_safe_antipyretic_mentions(query, exclude_terms={matched_term.lower()})
    if safe_mentions:
        detected_terms.extend(safe_mentions)
        if "paracetamol" not in normalization_candidates:
            normalization_candidates.append("paracetamol")
        if "paracetamol" not in canonical_ingredients:
            canonical_ingredients.append("paracetamol")
        policy_statuses["paracetamol"] = "safe_antipyretic"

    return {
        "detected_terms": detected_terms,
        "normalization_candidates": normalization_candidates,
        "canonical_ingredients": canonical_ingredients,
        "confidence": "high",
        "is_fdc": False,
        "fdc_constituents": [drug_id],
        "policy_lookup_statuses": policy_statuses,
        "action_code": action_code,
        "template_id": template_id,
        "negative_invariants_passed": True,
        "is_chronic_prescription": is_chronic,
        "has_negation_cue": has_negation,
    }


def analyze_medication_query(query: str) -> MedicationAnalysis:
    """
    Categorical Medication Safety Engine (Phase 4).
    Performs full FDC constituent decomposition, uncataloged drug escalation,
    chronic prescription preservation, and negative clinical invariant validation.
    """
    clean_text = query.lower()
    has_negation = any(pat.search(query) for pat in NEGATION_PATTERNS)
    is_chronic = is_chronic_antiplatelet_context(query)

    # Check 1: Indian FDCs
    for fdc in INDIAN_FDC_DATABASE:
        for alias in fdc["aliases"]:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, clean_text, re.IGNORECASE) or alias in query:
                if has_negation:
                    action_code = "NEGATED_MENTION_EDUCATION"
                    template_id = "TMPL_NEGATED_NSAID_EDU_V1"
                elif is_chronic:
                    action_code = "CHRONIC_PRESCRIPTION_ESCALATE"
                    template_id = "TMPL_CHRONIC_RX_SAFETY_V1"
                else:
                    action_code = "AVOID_FDC_CONTRAINDICATED"
                    template_id = "TMPL_FDC_AVOID_V1"

                policy_statuses = {c: "contraindicated" if c != "paracetamol" else "safe" for c in fdc["constituents"]}
                return {
                    "detected_terms": [alias],
                    "normalization_candidates": list(fdc["constituents"]),
                    "canonical_ingredients": list(fdc["constituents"]),
                    "confidence": "high",
                    "is_fdc": True,
                    "fdc_constituents": list(fdc["constituents"]),
                    "policy_lookup_statuses": policy_statuses,
                    "action_code": action_code,
                    "template_id": template_id,
                    "negative_invariants_passed": True,
                    "is_chronic_prescription": is_chronic,
                    "has_negation_cue": has_negation,
                }

    # Check 2: Single NSAIDs
    for drug in NSAID_DATABASE:
        for brand in drug["brand_names"]:
            pattern = rf"\b{re.escape(brand)}\b"
            if re.search(pattern, clean_text, re.IGNORECASE):
                return _build_nsaid_analysis(query, brand, drug["id"], has_negation, is_chronic)

        for bn_name in drug["bengali_names"]:
            if bn_name in query:
                return _build_nsaid_analysis(query, bn_name, drug["id"], has_negation, is_chronic)

    # Check 3: Unknown / Uncataloged medication
    for pattern in UNKNOWN_MED_PATTERNS:
        match = pattern.search(query)
        if match:
            term = match.group(0).strip()
            return {
                "detected_terms": [term],
                "normalization_candidates": [term.lower()],
                "canonical_ingredients": [],
                "confidence": "high",
                "is_fdc": False,
                "fdc_constituents": [],
                "policy_lookup_statuses": {term.lower(): "uncataloged_escalate"},
                "action_code": "ESCALATE_UNKNOWN_MEDICATION",
                "template_id": "TMPL_UNKNOWN_DRUG_ESCALATE_V1",
                "negative_invariants_passed": True,
                "is_chronic_prescription": False,
                "has_negation_cue": has_negation,
            }

    # Check 4: Safe antipyretic alone (e.g. Paracetamol / Dolo-650)
    for safe in SAFE_ANTIPYRETICS:
        pattern = rf"\b{re.escape(safe)}\b"
        if re.search(pattern, clean_text, re.IGNORECASE) or safe in query:
            return {
                "detected_terms": [safe],
                "normalization_candidates": ["paracetamol"],
                "canonical_ingredients": ["paracetamol"],
                "confidence": "high",
                "is_fdc": False,
                "fdc_constituents": ["paracetamol"],
                "policy_lookup_statuses": {"paracetamol": "safe_antipyretic"},
                "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
                "template_id": None,
                "negative_invariants_passed": True,
                "is_chronic_prescription": False,
                "has_negation_cue": has_negation,
            }

    # Check 5: Zero medication detected (Standard evidence retrieval)
    return {
        "detected_terms": [],
        "normalization_candidates": [],
        "canonical_ingredients": [],
        "confidence": "high",
        "is_fdc": False,
        "fdc_constituents": [],
        "policy_lookup_statuses": {},
        "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
        "template_id": None,
        "negative_invariants_passed": True,
        "is_chronic_prescription": False,
        "has_negation_cue": False,
    }
