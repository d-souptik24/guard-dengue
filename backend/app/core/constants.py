"""
GuardDengue — Clinical Core Constants & Controlled Vocabularies

Grounded in WHO Clinical Guidelines (2024), NCVBDC Protocols,
and GuardDengue Plan Version 2.
"""

# ─── Controlled 13-Topic Clinical Taxonomy ──────────────────────────────────
# Every guideline chunk and educational query maps to at least one of these labels.
CONTROLLED_TOPICS = frozenset({
    "Dengue basics",
    "Transmission",
    "Symptoms",
    "Prevention",
    "Hydration",
    "Warning signs",
    "Diagnosis",
    "Myths",
    "Children",
    "Pregnancy",
    "Medication safety",
    "Outbreak awareness",
    "Emergency guidance",
})

# ─── GRADE Certainty Levels ──────────────────────────────────────────────────
EVIDENCE_LEVELS = frozenset({
    "Level 1 (Global Clinical Practice Guideline)",
    "Level 2 (National Public Health Protocol)",
    "Level 2 (National Clinical Laboratory Protocol)",
    "Level 2 (Specialist Consensus Guideline)",
    "Level 3 (Public Health Operational Standard)",
    "ungraded",
})

# ─── Telephony & Emergency Contacts (West Bengal & National) ─────────────────
EMERGENCY_CONTACTS = {
    "ambulance": "108",
    "hospital_transfer": "102",
    "swasthya_bhawan": "1800-313-444-222",
    "tele_counseling": "033-2333-0100",
}

# ─── Statutory Medical Disclaimer (Bilingual) ─────────────────────────────────
DISCLAIMER_EN = (
    "This is general health awareness information, not an individual clinical diagnosis, "
    "prescription, or treatment plan. In case of emergency or severe warning signs, consult a "
    "registered doctor or call 108 immediately."
)

DISCLAIMER_BN = (
    "এটি একটি সাধারণ স্বাস্থ্য সচেতনতামূলক তথ্য, ব্যক্তিগত চিকিৎসা প্রেসক্রিপশন বা রোগ নির্ণয় নয়। "
    "জরুরী পরিস্থিতি বা গুরুতর সতর্কতামূলক লক্ষণ দেখা দিলে সরাসরি রেজিস্টার্ড চিকিৎসকের পরামর্শ নিন "
    "বা অবিলম্বে ১০৮ নম্বরে যোগাযোগ করুন।"
)
