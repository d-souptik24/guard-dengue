"""
GuardDengue — Unit Tests: Categorical Medication Safety Registry (Phase 4)

Tests:
1. Single NSAID Contraindication & Bengali Transliteration
2. Indian Fixed-Dose Combination (FDC) Constituent Decomposition (Combiflam, Zerodol-P, Meftal-Spas, Sumo)
3. Chronic Antiplatelet Prescription Protection (Life-preserving daily aspirin for stent/cardiac)
4. Negated Mention Educational Reinforcement (Cessation confirmed, reassurance given)
5. Unknown / Uncataloged Medication Fail-Closed Escalation (AyurDengue-Kadha, miracle drops)
6. Safe Antipyretic Handling (Paracetamol / Dolo)
7. Zero-Drug Clinical Query Control
8. Backward compatibility for detect_nsaid() Zone 2 screener contract
"""
import pytest
from app.safety.drug_registry import (
    detect_nsaid,
    analyze_medication_query,
    NSAID_DATABASE,
    INDIAN_FDC_DATABASE,
)

def test_single_nsaid_contraindication_english():
    res = analyze_medication_query("Can I take Brufen for severe headache and body pain?")
    assert res["action_code"] == "AVOID_NSAID_CONTRAINDICATED"
    assert res["template_id"] == "TMPL_NSAID_AVOID_V1"
    assert "ibuprofen" in res["canonical_ingredients"]
    assert res["is_fdc"] is False
    assert res["negative_invariants_passed"] is True
    assert res["is_chronic_prescription"] is False

def test_single_nsaid_contraindication_bengali():
    res = analyze_medication_query("আমার প্রচণ্ড জ্বর, আমি কি অ্যাসপিরিন খেতে পারি?")
    assert res["action_code"] == "AVOID_NSAID_CONTRAINDICATED"
    assert "aspirin" in res["canonical_ingredients"]
    assert res["negative_invariants_passed"] is True

def test_indian_fdc_combiflam_decomposition():
    res = analyze_medication_query("Can I take Combiflam for high fever and joint pain?")
    assert res["action_code"] == "AVOID_FDC_CONTRAINDICATED"
    assert res["template_id"] == "TMPL_FDC_AVOID_V1"
    assert res["is_fdc"] is True
    assert "ibuprofen" in res["fdc_constituents"]
    assert "paracetamol" in res["fdc_constituents"]
    assert res["policy_lookup_statuses"]["ibuprofen"] == "contraindicated"
    assert res["policy_lookup_statuses"]["paracetamol"] == "safe"
    assert res["negative_invariants_passed"] is True

def test_indian_fdc_zerodol_p_decomposition():
    res = analyze_medication_query("Doctor gave me Zerodol P for back ache, can I take it in dengue?")
    assert res["action_code"] == "AVOID_FDC_CONTRAINDICATED"
    assert res["is_fdc"] is True
    assert "aceclofenac" in res["fdc_constituents"]
    assert "paracetamol" in res["fdc_constituents"]

def test_indian_fdc_meftal_spas_decomposition():
    res = analyze_medication_query("Can I take Meftal Spas for stomach cramps with dengue?")
    assert res["action_code"] == "AVOID_FDC_CONTRAINDICATED"
    assert res["is_fdc"] is True
    assert "mefenamic_acid" in res["fdc_constituents"]
    assert "dicyclomine" in res["fdc_constituents"]

def test_indian_fdc_sumo_decomposition():
    res = analyze_medication_query("Can I take Sumo tablet for fever?")
    assert res["action_code"] == "AVOID_FDC_CONTRAINDICATED"
    assert res["is_fdc"] is True
    assert "nimesulide" in res["fdc_constituents"]

def test_chronic_prescription_protection():
    res = analyze_medication_query("My cardiologist prescribed daily aspirin for my heart stent, should I stop it?")
    assert res["action_code"] == "CHRONIC_PRESCRIPTION_ESCALATE"
    assert res["template_id"] == "TMPL_CHRONIC_RX_SAFETY_V1"
    assert res["is_chronic_prescription"] is True
    assert res["negative_invariants_passed"] is True

def test_negated_mention_education():
    res = analyze_medication_query("I stopped taking Combiflam yesterday after learning about dengue risk")
    assert res["action_code"] == "NEGATED_MENTION_EDUCATION"
    assert res["template_id"] == "TMPL_NEGATED_NSAID_EDU_V1"
    assert res["has_negation_cue"] is True
    assert res["negative_invariants_passed"] is True

def test_unknown_medication_fail_closed_escalation():
    res = analyze_medication_query("Can I drink AyurDengue-Kadha to boost my platelets?")
    assert res["action_code"] == "ESCALATE_UNKNOWN_MEDICATION"
    assert res["template_id"] == "TMPL_UNKNOWN_DRUG_ESCALATE_V1"
    assert res["negative_invariants_passed"] is True
    assert "ayurdengue-kadha" in res["detected_terms"][0].lower()
    assert res["canonical_ingredients"] == []


def test_negated_nsaid_with_safe_paracetamol_co_detection():
    res = analyze_medication_query(
        "I stopped taking Brufen yesterday when fever started, can I now safely take paracetamol?"
    )
    assert res["action_code"] == "NEGATED_MENTION_EDUCATION"
    assert res["has_negation_cue"] is True
    assert set(t.lower() for t in res["detected_terms"]) == {"brufen", "paracetamol"}
    assert set(res["canonical_ingredients"]) == {"ibuprofen", "paracetamol"}
    assert res["policy_lookup_statuses"]["ibuprofen"] == "contraindicated"
    assert res["policy_lookup_statuses"]["paracetamol"] == "safe_antipyretic"

def test_safe_antipyretic_paracetamol():
    res = analyze_medication_query("Can I take Paracetamol 650mg or Dolo-650 for fever?")
    assert res["action_code"] == "STANDARD_EVIDENCE_RETRIEVAL"
    assert res["template_id"] is None
    assert "paracetamol" in res["canonical_ingredients"]

def test_zero_drug_query_control():
    res = analyze_medication_query("Patient has severe abdominal pain and persistent vomiting")
    assert res["action_code"] == "STANDARD_EVIDENCE_RETRIEVAL"
    assert res["detected_terms"] == []
    assert res["canonical_ingredients"] == []

def test_detect_nsaid_backward_compatibility():
    match = detect_nsaid("Patient took Combiflam for fever")
    assert match is not None
    assert match["matched_term"] == "combiflam"
    assert "Ibuprofen" in match["generic_name"]
    assert match["is_chronic_context"] is False
    assert match["is_fdc"] is True
    assert match["fdc_constituents"] == ["ibuprofen", "paracetamol"]
