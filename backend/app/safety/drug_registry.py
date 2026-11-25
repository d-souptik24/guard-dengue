"""
GuardDengue — Bilingual NSAID and Medication Registry (Zone 2)

Curated list of contraindicated Non-Steroidal Anti-Inflammatory Drugs (NSAIDs),
common brand names in West Bengal/India, and Bengali transliterations.
Also provides heuristic detection for chronic prescription context.
"""
import re
from typing import TypedDict

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
        "brand_names": ["aspirin", "acetylsalicylic acid", "disprin", "ecosprin", "asprin", "delisprin"],
        "bengali_names": ["অ্যাসপিরিন", "এসপিরিন", "ডিসপ্রিন", "ইকোস্প্রিন", "অ্যাসপ্রিন"],
        "risk_level": "STRICTLY_CONTRAINDICATED"
    },
    {
        "id": "ibuprofen",
        "generic_name": "Ibuprofen",
        "brand_names": ["ibuprofen", "brufen", "combiflam", "advil", "motrin", "ibugesic", "flexon"],
        "bengali_names": ["আইবুপ্রোফেন", "ব্রুফেন", "কম্বিফ্লাম", "আইবুজেসিক", "ফ্লেক্সন"],
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
        "brand_names": ["mefenamic acid", "meftal", "meftal-spas", "ponstan", "mefkind"],
        "bengali_names": ["মেফেনামিক অ্যাসিড", "মেফট্যাল", "মেফট্যাল স্পাস", "মেফকাইন্ড"],
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
    }
]

SAFE_ANTIPYRETICS = [
    "paracetamol", "acetaminophen", "calpol", "crocin", "dolo", "dolo-650", "pacimol", "p-500", "p-650",
    "প্যারাসিটামল", "ক্রোসিন", "ডলো", "ক্যালপল"
]

# Regular expressions for chronic prescription detection
CHRONIC_RX_PATTERNS = [
    re.compile(r"\b(doctor|physician|dr|cardiologist|dr\.)\s+(prescribed|advised|told|gave|recommended)\b", re.IGNORECASE),
    re.compile(r"\b(daily|routine|regular|maintenance|ongoing)\s+(aspirin|ecosprin|medication|tablet|pill|dose)\b", re.IGNORECASE),
    re.compile(r"\b(heart|cardiac|stent|stroke|bypass|blood\s*pressure|hypertension)\b", re.IGNORECASE),
    re.compile(r"(ডাক্তার|চিকিৎসক)\s*(দিয়েছেন|বলেছেন|প্রেসক্রাইব)", re.IGNORECASE),
    re.compile(r"(হার্ট|হৃদরোগ|রক্তচাপ|প্রেসার|নিয়মিত)", re.IGNORECASE),
]

def detect_nsaid(query: str) -> dict | None:
    """
    Scans citizen query for contraindicated NSAIDs in English and Bengali.
    Returns matched drug record and whether chronic context is indicated.
    """
    clean_text = query.lower()
    
    # Check for chronic prescription indicators
    chronic_context = any(pattern.search(query) for pattern in CHRONIC_RX_PATTERNS)
    
    for drug in NSAID_DATABASE:
        # Match generic or brand names
        for brand in drug["brand_names"]:
            pattern = rf"\b{re.escape(brand)}\b"
            if re.search(pattern, clean_text, re.IGNORECASE):
                return {
                    "drug_id": drug["id"],
                    "generic_name": drug["generic_name"],
                    "matched_term": brand,
                    "risk_level": drug["risk_level"],
                    "is_chronic_context": chronic_context,
                }
        
        # Match Bengali names
        for bn_name in drug["bengali_names"]:
            if bn_name in query:
                return {
                    "drug_id": drug["id"],
                    "generic_name": drug["generic_name"],
                    "matched_term": bn_name,
                    "risk_level": drug["risk_level"],
                    "is_chronic_context": chronic_context,
                }
                
    return None
