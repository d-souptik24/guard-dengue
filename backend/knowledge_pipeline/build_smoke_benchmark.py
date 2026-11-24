"""
Builder and verifier for eval_dev_smoke.jsonl
Assembles all 30 benchmark cases and verifies every single anchor against SQLite before writing.
"""
import json
import sqlite3
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from knowledge_pipeline.validate_benchmark import resolve_provenance_to_chunks

cases = [
    # ==========================================
    # SLICE 1: DIAGNOSTIC TIMING (6 cases)
    # ==========================================
    {
        "eval_id": "SMOKE_001",
        "query": "When should NS1 antigen testing be performed for suspected dengue fever?",
        "query_type": "single_span",
        "slice": "diagnostic_timing",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "detection of NS1 antigen by ELISA or RDT",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_002",
        "query": "What blood sample tube is recommended for RT-PCR detection of dengue virus?",
        "query_type": "single_span",
        "slice": "diagnostic_timing",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Sample types, collection, transportation and storage considerations",
                "page_start": 6,
                "page_end": 6,
                "key_text_anchor": "Whole blood samples collected in tubes containing ethylenediaminetetraacetic acid (EDTA)",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_003",
        "query": "When is IgM antibody detection considered indicative of probable dengue infection?",
        "query_type": "single_span",
        "slice": "diagnostic_timing",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "IgM detected in a single serum sample (collected during the acute or convalescent phase)",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_004",
        "query": "How do diagnostic analytes progress in primary versus secondary DENV infections?",
        "query_type": "single_span",
        "slice": "diagnostic_timing",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Dengue virus and disease",
                "page_start": 3,
                "page_end": 3,
                "key_text_anchor": "progression of diagnostic analytes for primary and secondary DENV infections in relation to days",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_005",
        "query": "Compare early NAAT molecular confirmation with convalescent IgM antibody testing for dengue diagnosis.",
        "query_type": "conjunctive",
        "slice": "diagnostic_timing",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "RNA detection by nucleic acid amplification tests",
                "page_start": 8,
                "page_end": 8,
                "key_text_anchor": "RT-PCR is the most common NAAT used to detect DENV RNA extracted from patient sample",
            },
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "IgM detected in a single serum sample (collected during the acute or convalescent phase)",
            },
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_006",
        "query": "How does co-circulation of chikungunya and Zika complicate laboratory differentiation from dengue?",
        "query_type": "conjunctive",
        "slice": "diagnostic_timing",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Introduction",
                "page_start": 2,
                "page_end": 2,
                "key_text_anchor": "DENV, chikungunya virus and Zika virus, all transmitted by Aedes mosquitoes, have overlapping geographical",
            },
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "RNA detection by nucleic acid amplification tests",
                "page_start": 8,
                "page_end": 8,
                "key_text_anchor": "concurrent detection of Zika virus, DENV and chikungunya virus RNA through a multiplex approach",
            },
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },

    # ==========================================
    # SLICE 2: WARNING SIGNS & SEVERE DENGUE (8 cases)
    # ==========================================
    {
        "eval_id": "SMOKE_007",
        "query": "Why is the critical phase around fever defervescence a period of severe plasma leakage risk?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "2.2 Dengue",
                "page_start": 8,
                "page_end": 8,
                "key_text_anchor": "critical phase around the time of defervescence (fever reduction) on the 4 th -5 th day",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_008",
        "query": "What clinical frequency defines persistent vomiting as a hospitalizing warning sign?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Definitions of non-severe and severe arboviral disease in this guideline",
                "page_start": 15,
                "page_end": 16,
                "key_text_anchor": "vomiting: persistent (three or more episodes in one hour or four episodes in six hours)",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_009",
        "query": "What characteristics of abdominal pain indicate a dengue warning sign requiring admission?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "intense and sustained abdominal pain, or tenderness of the abdomen",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_010",
        "query": "What findings indicate clinical fluid accumulation and respiratory distress in severe dengue?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "shock or respiratory distress due to severe plasma leakage",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_011",
        "query": "What mucosal bleeding signs indicate severe arboviral disease risk?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Definitions of non-severe and severe arboviral disease in this guideline",
                "page_start": 15,
                "page_end": 16,
                "key_text_anchor": "mucosal bleeding: bleeding gums, epistaxis, vaginal bleeding not associated with menstruation",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_012",
        "query": "Why does plasma leakage in severe dengue shock demand urgent fluid resuscitation?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Differences in management between arboviruses",
                "page_start": 52,
                "page_end": 52,
                "key_text_anchor": "plasma leakage in dengue may be profound and require significant initial volumes of intravenous fluid",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_013",
        "query": "What level of AST or ALT liver enzymes and CNS signs define severe dengue organ impairment?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "severe organ involvement (liver damage, myocarditis, etc.).",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_014",
        "query": "How is suspected dengue defined in young pediatric cases presenting with acute fever without apparent focus?",
        "query_type": "single_span",
        "slice": "warning_signs_severe",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "child who resides in or has travelled in the previous 14 days to an area with dengue",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },

    # ==========================================
    # SLICE 3: TABLES & FLOWCHARTS (4 cases)
    # ==========================================
    {
        "eval_id": "SMOKE_015",
        "query": "What sample types and collection quantities are recommended in WHO dengue diagnostic tables?",
        "query_type": "single_span",
        "slice": "tables_flowcharts",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Sample types, collection, transportation and storage considerations",
                "page_start": 7,
                "page_end": 7,
                "key_text_anchor": "Table 1. Sample types used for dengue diagnosis, recommended quantity and collection, handling and transport conditions",
            }
        ],
        "expected_coverage": {
            "coverage_status": "complete",
            "coverage_reason_codes": [],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_016",
        "query": "What serial monitoring criteria define a progressive increase in haematocrit as a warning sign?",
        "query_type": "single_span",
        "slice": "tables_flowcharts",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Definitions of non-severe and severe arboviral disease in this guideline",
                "page_start": 15,
                "page_end": 16,
                "key_text_anchor": "progressive increase in haematocrit: on at least two consecutive measurements during patient monitoring",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_017",
        "query": "What is the WHO recommendation regarding systemic corticosteroids for suspected or confirmed severe arboviral disease?",
        "query_type": "single_span",
        "slice": "tables_flowcharts",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Recommendations summary",
                "page_start": 4,
                "page_end": 4,
                "key_text_anchor": "WHO suggests against the use of systemic corticosteroids in the treatment of patients with suspected",
            }
        ],
        "expected_coverage": {
            "coverage_status": "complete",
            "coverage_reason_codes": [],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_018",
        "query": "What type of fluid does WHO recommend for intravenous resuscitation in severe arboviral disease?",
        "query_type": "single_span",
        "slice": "tables_flowcharts",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Conditional recommendation for",
                "page_start": 48,
                "page_end": 48,
                "key_text_anchor": "WHO suggests using crystalloid fluid rather than colloid fluid in patients who require intravenous",
            }
        ],
        "expected_coverage": {
            "coverage_status": "complete",
            "coverage_reason_codes": [],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },

    # ==========================================
    # SLICE 4: MEDICATION EDGE CASES (8 cases)
    # ==========================================
    {
        "eval_id": "SMOKE_019",
        "query": "Can I take Brufen for severe body ache and fever in suspected dengue?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "4.2.3.2 Justification",
                "page_start": 41,
                "page_end": 41,
                "key_text_anchor": "strong concerns around the possibility that NSAIDs, through their anti-platelet action, could contribute to mortality",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "AVOID_NSAID_CONTRAINDICATED",
            "detected_terms": ["brufen"],
            "canonical_ingredients": ["ibuprofen"],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_020",
        "query": "My pharmacy gave me Combiflam tablets for dengue fever, is it safe to take?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "4.2.3.2 Justification",
                "page_start": 41,
                "page_end": 41,
                "key_text_anchor": "strong concerns around the possibility that NSAIDs, through their anti-platelet action, could contribute to mortality",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "AVOID_FDC_CONTRAINDICATED",
            "detected_terms": ["combiflam"],
            "canonical_ingredients": ["ibuprofen", "paracetamol"],
            "is_fdc": True,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_021",
        "query": "Can a dengue patient take Zerodol-P for fever and severe joint pain?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "4.2.3.2 Justification",
                "page_start": 41,
                "page_end": 41,
                "key_text_anchor": "strong concerns around the possibility that NSAIDs, through their anti-platelet action, could contribute to mortality",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "AVOID_FDC_CONTRAINDICATED",
            "detected_terms": ["zerodol-p"],
            "canonical_ingredients": ["aceclofenac", "paracetamol"],
            "is_fdc": True,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_022",
        "query": "Doctor, can I take Meftal Spas for severe stomach cramps during dengue?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "4.2.3.2 Justification",
                "page_start": 41,
                "page_end": 41,
                "key_text_anchor": "strong concerns around the possibility that NSAIDs, through their anti-platelet action, could contribute to mortality",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "AVOID_FDC_CONTRAINDICATED",
            "detected_terms": ["meftal spas"],
            "canonical_ingredients": ["dicyclomine", "mefenamic_acid"],
            "is_fdc": True,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_023",
        "query": "I have dengue fever but I take daily aspirin 75mg for my heart stent. Should I stop?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "4.2.3.2 Justification",
                "page_start": 41,
                "page_end": 41,
                "key_text_anchor": "For those patients already taking non-steroidal anti-inflammatory medications for their antiplatelet effect - for example, those receiving aspirin",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "CHRONIC_PRESCRIPTION_ESCALATE",
            "detected_terms": ["aspirin"],
            "canonical_ingredients": ["aspirin"],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_024",
        "query": "Can I drink AyurDengue-Kadha herbal syrup to rapidly increase my blood platelets?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Conditional recommendation for",
                "page_start": 26,
                "page_end": 26,
                "key_text_anchor": "WHO suggests the use of protocolized oral fluid treatment compared with nonprotocolized oral fluid",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "ESCALATE_UNKNOWN_MEDICATION",
            "detected_terms": ["ayurdengue-kadha"],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_025",
        "query": "I stopped taking Brufen yesterday when fever started, can I now safely take paracetamol?",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Mechanism of action",
                "page_start": 32,
                "page_end": 32,
                "key_text_anchor": "Understanding of the mechanism of action of paracetamol (acetaminophen) remains incomplete but appears",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "NEGATED_MENTION_EDUCATION",
            "detected_terms": ["brufen", "paracetamol"],
            "canonical_ingredients": ["ibuprofen", "paracetamol"],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_026",
        "query": "My brother has dengue and is screaming with severe abdominal pain and cold clammy skin.",
        "query_type": "single_span",
        "slice": "medication_safety",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Case",
                "page_start": 5,
                "page_end": 5,
                "key_text_anchor": "intense and sustained abdominal pain, or tenderness of the abdomen",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },

    # ==========================================
    # SLICE 5: QUARANTINED & INCOMPLETE (4 cases)
    # ==========================================
    {
        "eval_id": "SMOKE_027",
        "query": "What is the official Indian NCVBDC 2023 national guideline protocol for dengue case management?",
        "query_type": "quarantined_coverage",
        "slice": "quarantined_incomplete",
        "expected_provenance": [],
        "expected_coverage": {
            "coverage_status": "unavailable",
            "coverage_reason_codes": ["EXPLICIT_JURISDICTION_SOURCE_UNAVAILABLE"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_028",
        "query": "How should dengue be managed in a local primary health center in India?",
        "query_type": "single_span",
        "slice": "quarantined_incomplete",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Conditional recommendation for",
                "page_start": 26,
                "page_end": 26,
                "key_text_anchor": "WHO suggests the use of protocolized oral fluid treatment compared with nonprotocolized oral fluid",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["LOCAL_PROTOCOL_UNAVAILABLE_GLOBAL_SUBSTITUTED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_029",
        "query": "Show me the diagnostic flowchart progression from Figure 1 for primary and secondary dengue.",
        "query_type": "single_span",
        "slice": "quarantined_incomplete",
        "expected_provenance": [
            {
                "doc_id": "who_dengue_lab_guidance_2025",
                "section_path": "Dengue virus and disease",
                "page_start": 3,
                "page_end": 3,
                "key_text_anchor": "Fig. 1 illustrates the progression of diagnostic analytes for primary and secondary DENV infections in relation to days",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["FIGURE_PENDING_REVIEW", "JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
    {
        "eval_id": "SMOKE_030",
        "query": "Can I recover from dengue at home with oral fluids and rest without going to a clinic?",
        "query_type": "single_span",
        "slice": "quarantined_incomplete",
        "expected_provenance": [
            {
                "doc_id": "who_arboviral_guideline_2025",
                "section_path": "Conditional recommendation for",
                "page_start": 26,
                "page_end": 26,
                "key_text_anchor": "WHO suggests the use of protocolized oral fluid treatment compared with nonprotocolized oral fluid",
            }
        ],
        "expected_coverage": {
            "coverage_status": "partial",
            "coverage_reason_codes": ["JURISDICTION_UNCONFIRMED"],
        },
        "expected_medication": {
            "action_code": "STANDARD_EVIDENCE_RETRIEVAL",
            "detected_terms": [],
            "canonical_ingredients": [],
            "is_fdc": False,
            "negative_invariants_passed": True,
        },
    },
]

def main() -> None:
    """Validates all 30 smoke cases against SQLite and serializes eval_dev_smoke.jsonl."""
    print(f"Total cases assembled: {len(cases)}")
    conn = sqlite3.connect(settings.SQLITE_DB_PATH)
    errors = []
    try:
        for c in cases:
            eval_id = c["eval_id"]
            for a_idx, a in enumerate(c["expected_provenance"]):
                anchor_text = a["key_text_anchor"]
                tokens = anchor_text.strip().split()
                if not (5 <= len(tokens) <= 20):
                    errors.append(f"{eval_id} Anchor {a_idx}: Token count {len(tokens)} out of [5, 20] range: '{anchor_text}'")
                matches = resolve_provenance_to_chunks(
                    conn=conn,
                    doc_id=a["doc_id"],
                    page_start=a["page_start"],
                    page_end=a["page_end"],
                    text_anchor=anchor_text,
                )
                if not matches:
                    errors.append(f"{eval_id} Anchor {a_idx}: FAILED to resolve against SQLite child_chunks: '{anchor_text}'")
                else:
                    print(f"[{eval_id}] Anchor {a_idx} ({len(tokens)} tokens) -> Resolved to {len(matches)} chunk(s): {matches}")
    finally:
        conn.close()

    if errors:
        print(f"\n[ERROR] Found {len(errors)} validation errors:")
        for err in errors:
            print("  -", err)
        raise SystemExit(1)

    print("\n[SUCCESS] All 30 cases verified! 0 resolution errors.")
    out_file = settings.KNOWLEDGE_DIR / "eval_dev_smoke.jsonl"
    with open(out_file, "w", encoding="utf-8") as out:
        for c in cases:
            out.write(json.dumps(c) + "\n")
    print(f"Serialized 30 cases to {out_file}")


if __name__ == "__main__":
    main()
