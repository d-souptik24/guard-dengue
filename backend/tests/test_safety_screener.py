"""
GuardDengue — Unit Tests: Zone 2 Clinical Safety Screener

Tests deterministic sub-20ms screening for:
1. Emergency red flags (urgent triage with 108 telephony action).
2. Contraindicated NSAIDs in English and Bengali.
3. Chronic prescription caveat detection.
4. Out-of-scope non-dengue detection.
"""
import pytest
from app.safety.screener import screen_query
from app.safety.drug_registry import detect_nsaid

def test_screener_red_flag_abdominal_pain():
    query = "Patient has 103 fever and severe abdominal pain with persistent vomiting"
    decision = screen_query(query, language="en")
    assert decision.route == "urgent"
    assert decision.dial_108 is True
    assert decision.telephony_action is not None
    assert decision.telephony_action["number"] == "108"
    assert any("RED_FLAG" in r for r in decision.matched_rules)
    assert decision.zone2_latency_ms < 20.0
    assert "EMERGENCY WARNING" in decision.direct_template

def test_screener_red_flag_bleeding_gums():
    query = "I notice bleeding from my gums and black stool after 4 days of fever"
    decision = screen_query(query, language="en")
    assert decision.route == "urgent"
    assert decision.dial_108 is True
    assert "Call 108" in decision.direct_template

def test_screener_red_flag_bengali():
    query = "রোগীর তীব্র পেটে ব্যথা এবং মাড়ি থেকে রক্ত পড়ছে"
    decision = screen_query(query, language="bn")
    assert decision.route == "urgent"
    assert decision.dial_108 is True
    assert "১০৮" in decision.direct_template
    assert "জরুরী সতর্কতা" in decision.direct_template

def test_screener_nsaid_combiflam():
    query = "Can I take Combiflam or Brufen for high fever and joint pain?"
    decision = screen_query(query, language="en")
    assert decision.route == "medication"
    assert decision.dial_108 is False
    assert any("NSAID_CONTRAINDICATION" in r for r in decision.matched_rules)
    assert "DO NOT TAKE" in decision.direct_template
    assert "Paracetamol" in decision.direct_template
    assert decision.zone2_latency_ms < 20.0

def test_screener_nsaid_disprin():
    query = "Is Disprin safe for headache during dengue?"
    decision = screen_query(query, language="en")
    assert decision.route == "medication"
    assert "strictly contraindicated" in decision.direct_template.lower()

def test_screener_nsaid_bengali():
    query = "জ্বরের জন্য ব্রুফেন বা অ্যাসপিরিন খাওয়া যাবে কি?"
    decision = screen_query(query, language="bn")
    assert decision.route == "medication"
    assert "সম্পূর্ণ নিষিদ্ধ" in decision.direct_template
    assert "প্যারাসিটামল" in decision.direct_template

def test_screener_chronic_prescription_caveat():
    query = "My cardiologist prescribed daily 75mg aspirin for my heart stent. Now I have dengue, should I stop it?"
    decision = screen_query(query, language="en")
    assert decision.route == "medication"
    assert "CHRONIC_PRESCRIPTION_CAVEAT" in decision.matched_rules
    assert "REGULAR / CARDIAC MEDICATIONS" in decision.direct_template
    assert "Do NOT abruptly stop" in decision.direct_template

def test_screener_dengue_education():
    query = "What is the recommended fluid intake and hydration for dengue outpatient care?"
    decision = screen_query(query, language="en")
    assert decision.route == "education"
    assert decision.direct_template is None
    assert decision.dial_108 is False

def test_screener_out_of_scope():
    query = "How do I fix a leaking kitchen pipe and engine oil?"
    decision = screen_query(query, language="en")
    assert decision.route == "uncertain"
    assert "OUT_OF_SCOPE_QUERY" in decision.matched_rules
