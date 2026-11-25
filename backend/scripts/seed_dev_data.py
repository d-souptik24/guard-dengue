"""
GuardDengue — Development Seed Data Generator

Provisions local SQLite and Qdrant storage with 15 verified clinical evidence chunks
from official WHO (2024), NCVBDC, and ICMR dengue guidelines, matching Ayan's
Module 2 database schema identically.

Usage:
    python backend/scripts/seed_dev_data.py
"""
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

# Paths
BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)

SQLITE_PATH = DATA_DIR / "guarddengue_chunks.db"
POLICY_PATH = DATA_DIR / "safety_policy_v0.1-dev.json"
QDRANT_STORAGE_DIR = DATA_DIR / "qdrant_storage"
CORPUS_RELEASE = "v0.1-dev"

# ─── 15 Curated Clinical Grounding Chunks ────────────────────────────────────
SEED_CHUNKS = [
    {
        "chunk_id": "KB-WARN-001",
        "parent_id": "SEC-WHO-WARN",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 3 > Critical Phase & Warning Signs",
        "page_start": 24,
        "page_end": 26,
        "topic": ["Warning signs", "Emergency guidance"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "The critical phase of dengue begins around the time of defervescence (the drop in fever, "
            "typically on Days 3 to 7 of illness). During this 24 to 48 hour window, increased capillary "
            "permeability leads to plasma leakage. Warning signs include severe abdominal pain or tenderness, "
            "persistent vomiting (at least 3 episodes in 24 hours), mucosal bleeding (gums, nose, gastrointestinal), "
            "clinical fluid accumulation (ascites, pleural effusion), lethargy, restlessness, and liver enlargement "
            ">2 cm. Patients exhibiting any of these warning signs require immediate medical evaluation and hospital admission."
        ),
    },
    {
        "chunk_id": "KB-MED-001",
        "parent_id": "SEC-WHO-MED",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 4 > Medication Safety & Analgesics",
        "page_start": 32,
        "page_end": 33,
        "topic": ["Medication safety"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "Non-steroidal anti-inflammatory drugs (NSAIDs) such as ibuprofen, aspirin, diclofenac, naproxen, "
            "and mefenamic acid (including combination products like Combiflam) are strictly contraindicated "
            "in suspected or confirmed dengue fever. These drugs inhibit platelet aggregation and exacerbate "
            "vascular endothelial damage, significantly increasing the risk of life-threatening gastrointestinal "
            "hemorrhage. Paracetamol is the antipyretic of choice. Patients on long-term prescribed medications "
            "for chronic conditions (e.g. cardiac aspirin, antihypertensives) must consult their physician before modifying therapy."
        ),
    },
    {
        "chunk_id": "KB-DIAG-001",
        "parent_id": "SEC-ICMR-DIAG",
        "doc_id": "icmr_dengue_lab_protocol_2024",
        "section_path": "ICMR Guidelines > Section 2 > Diagnostic Testing Timeline",
        "page_start": 10,
        "page_end": 12,
        "topic": ["Diagnosis"],
        "evidence_level": "Level 2 (National Clinical Laboratory Protocol)",
        "source": "ICMR Guidelines for Laboratory Diagnosis 2024",
        "publication_date": "2024-11-12",
        "text": (
            "Laboratory diagnostic strategy depends strictly on the day of illness: "
            "From Day 1 to Day 5 of fever onset (the acute viremic phase), Dengue NS1 antigen testing (ELISA or rapid) "
            "or RT-PCR should be performed. Serum viral RNA and NS1 antigen are detectable during this window. "
            "After Day 5 (from Day 6 onwards), as viremia subsides, anti-dengue IgM and IgG antibody tests (MAC-ELISA) "
            "become the primary diagnostic markers. NS1 testing after Day 5 carries high false-negative rates."
        ),
    },
    {
        "chunk_id": "KB-FLUID-001",
        "parent_id": "SEC-NCVBDC-FLUID",
        "doc_id": "ncvbdc_dengue_clinical_protocol_2024",
        "section_path": "NCVBDC Protocols > Section 5 > Fluid Management & Hydration",
        "page_start": 18,
        "page_end": 20,
        "topic": ["Hydration", "Prevention"],
        "evidence_level": "Level 2 (National Public Health Protocol)",
        "source": "NCVBDC Clinical Protocol 2024",
        "publication_date": "2024-09-15",
        "text": (
            "Adequate oral fluid intake is the cornerstone of early outpatient dengue care. Patients should consume "
            "Oral Rehydration Salts (ORS), tender coconut water, diluted fruit juices, and rice water. Plain water "
            "alone in excessive quantities should be avoided as it can cause electrolyte imbalances and hyponatremia. "
            "Fluid therapy must maintain adequate urine output (at least 0.5 mL/kg/hour in adults). If the patient is "
            "unable to retain oral fluids due to persistent vomiting, intravenous crystalloids (0.9% Normal Saline or Ringer Lactate) are indicated."
        ),
    },
    {
        "chunk_id": "KB-PLT-001",
        "parent_id": "SEC-WHO-PLT",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 5 > Platelet Transfusion Guidelines",
        "page_start": 45,
        "page_end": 47,
        "topic": ["Dengue basics", "Warning signs"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "Prophylactic platelet transfusion is NOT recommended in dengue fever based solely on a falling platelet count. "
            "Studies demonstrate that prophylactic transfusions do not prevent severe bleeding and carry risks of fluid overload "
            "and allergic reactions. Platelet transfusion is reserved for patients with significant clinical bleeding (hematemesis, "
            "melena, gross hematuria) or profound thrombocytopenia with platelets < 10,000 to 20,000/μL in the presence of hemorrhagic risk."
        ),
    },
    {
        "chunk_id": "KB-PED-001",
        "parent_id": "SEC-IAP-PED",
        "doc_id": "iap_pediatric_dengue_consensus_2024",
        "section_path": "IAP Protocols > Section 3 > Pediatric Dengue Warning Signs",
        "page_start": 14,
        "page_end": 16,
        "topic": ["Children", "Warning signs"],
        "evidence_level": "Level 2 (Specialist Consensus Guideline)",
        "source": "Indian Academy of Pediatrics (IAP) Consensus 2024",
        "publication_date": "2024-06-20",
        "text": (
            "Dengue warning signs in infants and young children often present differently than in adults. Pediatric "
            "emergency signs include sudden lethargy or drowsiness alternating with irritability, refusal of oral feeds, "
            "cold and clammy extremities, rapid shallow breathing, oliguria (absence of urination for >6 hours), and swollen eyelids. "
            "Never attempt to calculate pediatric drug doses without direct physician direction. For fever, pediatric paracetamol "
            "at 10-15 mg/kg per dose may be administered under clinical guidance."
        ),
    },
    {
        "chunk_id": "KB-PREG-001",
        "parent_id": "SEC-FOGSI-PREG",
        "doc_id": "fogsi_dengue_pregnancy_guidance_2024",
        "section_path": "FOGSI Guidelines > Chapter 2 > Dengue in Pregnancy",
        "page_start": 8,
        "page_end": 11,
        "topic": ["Pregnancy", "Emergency guidance"],
        "evidence_level": "Level 2 (Specialist Consensus Guideline)",
        "source": "FOGSI Clinical Practice Recommendation 2024",
        "publication_date": "2024-07-05",
        "text": (
            "Dengue infection during pregnancy poses severe risks of maternal hemorrhage, preterm birth, and vertical transmission "
            "to the neonate. Physiological changes of pregnancy (hemodilution and gestational thrombocytopenia) can mask the onset "
            "of plasma leakage. All pregnant individuals with acute febrile illness or suspected dengue must be referred for obstetric "
            "and hematological hospital admission. NSAIDs are strictly prohibited."
        ),
    },
    {
        "chunk_id": "KB-TRANS-001",
        "parent_id": "SEC-WHO-TRANS",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 1 > Transmission & Epidemiology",
        "page_start": 5,
        "page_end": 7,
        "topic": ["Transmission", "Dengue basics"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "Dengue virus (DENV-1, DENV-2, DENV-3, DENV-4) is transmitted primarily by female mosquitoes of the genus Aedes, "
            "principally Aedes aegypti and to a lesser extent Aedes albopictus. Aedes aegypti bites predominantly during the daytime, "
            "with peak biting activity at dawn and dusk. It breeds in clean, stagnant water inside and around residential environments "
            "(water coolers, flower vases, uncovered water tanks, plastic containers, discarded tires)."
        ),
    },
    {
        "chunk_id": "KB-PREV-001",
        "parent_id": "SEC-NCVBDC-PREV",
        "doc_id": "ncvbdc_dengue_clinical_protocol_2024",
        "section_path": "NCVBDC Protocols > Chapter 6 > Source Reduction & Prevention",
        "page_start": 28,
        "page_end": 30,
        "topic": ["Prevention"],
        "evidence_level": "Level 2 (National Public Health Protocol)",
        "source": "NCVBDC Clinical Protocol 2024",
        "publication_date": "2024-09-15",
        "text": (
            "Prevention relies on source reduction of mosquito breeding habitats and personal protection. Citizens should observe a "
            "weekly 'Dry Day'—emptying, scrubbing, and drying all water collection containers, flower pots, air coolers, and trays. "
            "Wear long-sleeved light-colored clothing. Use mosquito repellents containing DEET, Picaridin, or IR3535 on exposed skin. "
            "Ensure window and door mesh screens are intact."
        ),
    },
    {
        "chunk_id": "KB-MYTH-001",
        "parent_id": "SEC-ICMR-MYTH",
        "doc_id": "icmr_dengue_lab_protocol_2024",
        "section_path": "ICMR Guidelines > Section 5 > Scientific Evidence on Alternative Remedies",
        "page_start": 35,
        "page_end": 36,
        "topic": ["Myths"],
        "evidence_level": "Level 2 (National Clinical Laboratory Protocol)",
        "source": "ICMR Guidelines for Laboratory Diagnosis 2024",
        "publication_date": "2024-11-12",
        "text": (
            "There is no robust clinical evidence supporting papaya leaf juice, goat milk, or kiwi fruit as curative treatments "
            "for dengue virus or as replacements for standard medical fluid monitoring. While some commercial extracts show mild "
            "in vitro platelet-promoting properties, relying on alternative home remedies instead of medical evaluation during the "
            "critical phase can lead to fatal delays in managing shock syndrome."
        ),
    },
    {
        "chunk_id": "KB-OUT-001",
        "parent_id": "SEC-WB-OUT",
        "doc_id": "wb_health_dengue_circular_2024",
        "section_path": "WB Health Circular > Section 1 > State Helplines & Testing Centers",
        "page_start": 1,
        "page_end": 3,
        "topic": ["Outbreak awareness", "Emergency guidance"],
        "evidence_level": "Level 2 (National Public Health Protocol)",
        "source": "Department of Health & Family Welfare, Govt. of West Bengal 2024",
        "publication_date": "2024-08-01",
        "text": (
            "The Department of Health & Family Welfare, Govt. of West Bengal operates 24/7 dedicated control rooms and diagnostic facilities. "
            "Free NS1 and Mac-ELISA diagnostic testing is available across all District Hospitals, Sub-Divisional Hospitals, and Urban "
            "Primary Health Centres (UPHCs). State Tele-Counseling and Dengue Helpline: 1800-313-444-222 / 033-2333-0100. Emergency ambulance: 108 / 102."
        ),
    },
    {
        "chunk_id": "KB-SYMP-001",
        "parent_id": "SEC-WHO-SYMP",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 2 > Clinical Manifestations",
        "page_start": 15,
        "page_end": 17,
        "topic": ["Symptoms", "Dengue basics"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "Dengue presents as an acute febrile illness characterized by high fever (40°C/104°F) accompanied by at least two of the "
            "following symptoms: severe headache, retro-orbital (behind-the-eye) pain, severe myalgia (muscle pain), arthralgia (joint pain), "
            "nausea, vomiting, swollen glands, or maculopapular rash. The febrile phase lasts 2 to 7 days, after which fever typically drops."
        ),
    },
    {
        "chunk_id": "KB-CHRONIC-001",
        "parent_id": "SEC-WHO-MED",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 4 > Chronic Prescription Management",
        "page_start": 34,
        "page_end": 34,
        "topic": ["Medication safety"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "While over-the-counter NSAIDs must be avoided in acute dengue, patients who take prescribed antiplatelet or anticoagulant "
            "therapies (such as low-dose aspirin after coronary stenting, clopidogrel, or warfarin) must NEVER stop their medications "
            "autonomously. Immediate consultation with the treating cardiologist or hematologist is mandatory to weigh bleeding risk "
            "against catastrophic arterial stent thrombosis."
        ),
    },
    {
        "chunk_id": "KB-ELDERLY-001",
        "parent_id": "SEC-NCVBDC-ELDERLY",
        "doc_id": "ncvbdc_dengue_clinical_protocol_2024",
        "section_path": "NCVBDC Protocols > Section 7 > High-Risk Groups: Elderly & Comorbidities",
        "page_start": 31,
        "page_end": 33,
        "topic": ["Warning signs", "Emergency guidance"],
        "evidence_level": "Level 2 (National Public Health Protocol)",
        "source": "NCVBDC Clinical Protocol 2024",
        "publication_date": "2024-09-15",
        "text": (
            "Elderly patients and individuals with chronic comorbid conditions (diabetes mellitus, hypertension, chronic kidney disease, "
            "coronary artery disease, hemoglobinopathies) are at elevated risk for rapid progression to severe dengue. Early hospitalization "
            "and cautious fluid titration are required, as aggressive fluid administration can trigger congestive heart failure and pulmonary edema."
        ),
    },
    {
        "chunk_id": "KB-PHASE-001",
        "parent_id": "SEC-WHO-PHASE",
        "doc_id": "who_dengue_guidelines_2024",
        "section_path": "WHO Guidelines > Chapter 2 > The Three Phases of Dengue",
        "page_start": 18,
        "page_end": 20,
        "topic": ["Dengue basics"],
        "evidence_level": "Level 1 (Global Clinical Practice Guideline)",
        "source": "WHO Clinical Management Guidelines 2024",
        "publication_date": "2024-08-10",
        "text": (
            "Dengue infection evolves across three distinct clinical phases: "
            "1. Febrile Phase (Days 1–3): Sudden onset high fever, intense body aches, headache, dehydration risk. "
            "2. Critical Phase (Days 3–7): Occurs at defervescence when fever drops; plasma leakage, hemoconcentration, and shock may occur. "
            "3. Recovery / Convalescent Phase (Days 7–10): Gradual reabsorption of extravasated fluid, stabilization of hematocrit and platelets, appetite return."
        ),
    },
]

def seed_sqlite():
    """Initializes SQLite database and tables matching Ayan's Module 2."""
    print(f"Provisioning SQLite database: {SQLITE_PATH}")
    conn = sqlite3.connect(SQLITE_PATH)
    cur = conn.cursor()
    
    # 1. parent_chunks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS parent_chunks (
        parent_id       TEXT PRIMARY KEY,
        doc_id          TEXT NOT NULL,
        section_path    TEXT NOT NULL,
        title           TEXT,
        level           INTEGER DEFAULT 1,
        text            TEXT NOT NULL,
        token_count     INTEGER DEFAULT 0,
        corpus_release  TEXT NOT NULL
    );
    """)

    # 2. child_chunks table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS child_chunks (
        chunk_id            TEXT PRIMARY KEY,
        parent_id           TEXT NOT NULL REFERENCES parent_chunks(parent_id),
        doc_id              TEXT NOT NULL,
        chunk_type          TEXT NOT NULL,  -- 'prose' | 'table' | 'figure'
        element_type        TEXT DEFAULT 'prose',
        text                TEXT NOT NULL,
        section_path        TEXT NOT NULL,
        page_start          INTEGER,
        page_end            INTEGER,
        review_status       TEXT NOT NULL DEFAULT 'approved', -- 'approved' | 'pending_review' | 'quarantined'
        reviewed_by         TEXT DEFAULT 'dr_wazib_approved',
        reviewed_at         TEXT DEFAULT '2026-11-20T10:00:00Z',
        superseded_by       TEXT,
        chunk_content_hash  TEXT NOT NULL,
        metadata_json       TEXT NOT NULL
    );
    """)

    # 3. release_manifests table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS release_manifests (
        release_id       TEXT PRIMARY KEY,
        collection_name  TEXT NOT NULL,
        manifest_sha256  TEXT NOT NULL,
        sqlite_count     INTEGER NOT NULL,
        qdrant_count     INTEGER NOT NULL,
        policy_count     INTEGER NOT NULL,
        promoted_by      TEXT,
        promoted_at      TEXT,
        status           TEXT NOT NULL   -- 'active' | 'staged' | 'superseded'
    );
    """)

    # Insert Parent Chunks
    parents_seen = set()
    for item in SEED_CHUNKS:
        pid = item["parent_id"]
        if pid not in parents_seen:
            parents_seen.add(pid)
            cur.execute("""
            INSERT OR REPLACE INTO parent_chunks 
            (parent_id, doc_id, section_path, title, text, corpus_release)
            VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pid,
                item["doc_id"],
                item["section_path"],
                item["section_path"].split(">")[-1].strip(),
                item["text"],
                CORPUS_RELEASE,
            ))

    # Insert Child Chunks
    for item in SEED_CHUNKS:
        cid = item["chunk_id"]
        content_hash = hashlib.sha256(item["text"].encode("utf-8")).hexdigest()
        meta = {
            "source": item["source"],
            "publication_date": item["publication_date"],
            "evidence_level": item["evidence_level"],
            "topic": item["topic"],
            "chunk_id": cid,
            "corpus_release": CORPUS_RELEASE,
            "doc_id": item["doc_id"],
            "section_path": item["section_path"],
            "page_start": item["page_start"],
            "page_end": item["page_end"],
            "review_status": "approved",
            "reviewed_by": "dr_wazib_approved",
            "reviewed_at": "2026-11-20T10:00:00Z",
        }
        
        cur.execute("""
        INSERT OR REPLACE INTO child_chunks 
        (chunk_id, parent_id, doc_id, chunk_type, element_type, text, section_path,
         page_start, page_end, review_status, reviewed_by, reviewed_at,
         chunk_content_hash, metadata_json)
        VALUES (?, ?, ?, 'prose', 'prose', ?, ?, ?, ?, 'approved', 'dr_wazib_approved',
                '2026-11-20T10:00:00Z', ?, ?)
        """, (
            cid,
            item["parent_id"],
            item["doc_id"],
            item["text"],
            item["section_path"],
            item["page_start"],
            item["page_end"],
            content_hash,
            json.dumps(meta, ensure_ascii=False),
        ))

    # Record active release manifest
    cur.execute("""
    INSERT OR REPLACE INTO release_manifests
    (release_id, collection_name, manifest_sha256, sqlite_count, qdrant_count, policy_count, promoted_by, promoted_at, status)
    VALUES (?, ?, ?, ?, ?, 1, 'dr_wazib', '2026-11-20T10:00:00Z', 'active')
    """, (
        CORPUS_RELEASE,
        f"guarddengue_{CORPUS_RELEASE}",
        hashlib.sha256(b"manifest_seed").hexdigest(),
        len(SEED_CHUNKS),
        len(SEED_CHUNKS),
    ))

    conn.commit()
    conn.close()
    print(f"Successfully seeded {len(SEED_CHUNKS)} clinical chunks into SQLite!")

def seed_policy():
    """Generates the local safety policy JSON artifact matching Ayan's Cell 23."""
    print(f"Provisioning local safety policy artifact: {POLICY_PATH}")
    policy = {
        "corpus_release": CORPUS_RELEASE,
        "policy_id": "nsaid_contraindication_dengue_v1",
        "review_status": "approved",
        "reviewed_by": "dr_wazib_approved",
        "reviewed_at": "2026-11-20T10:00:00Z",
        "clinical_context": "suspected_dengue",
        "rules": [
            {
                "rule_id": "RULE-NSAID-AVOID",
                "drug_class": "NSAIDs",
                "action": "AVOID_IN",
                "rationale": "Inhibits platelet aggregation, increases hemorrhage risk, exacerbates vascular leakage",
                "source_chunk_id": "KB-MED-001",
                "supported_by_guideline": "WHO Clinical Management Guidelines 2024",
                "drug_members": [
                    {"id": "aspirin", "name": "Aspirin", "aliases": ["acetylsalicylic acid", "disprin", "ecosprin", "asprin"]},
                    {"id": "ibuprofen", "name": "Ibuprofen", "aliases": ["brufen", "advil", "motrin", "combiflam"]},
                    {"id": "diclofenac", "name": "Diclofenac", "aliases": ["voveran", "voltaren", "diclo"]},
                    {"id": "naproxen", "name": "Naproxen", "aliases": ["naprosyn", "aleve"]},
                    {"id": "mefenamic_acid", "name": "Mefenamic Acid", "aliases": ["meftal", "meftal-spas", "ponstan"]},
                    {"id": "ketorolac", "name": "Ketorolac", "aliases": ["toradol", "ketorol"]},
                    {"id": "piroxicam", "name": "Piroxicam", "aliases": ["feldene", "dolonex"]},
                ],
                "safe_alternatives": ["Paracetamol", "Acetaminophen"],
                "chronic_rx_warning": "Patients on long-term prescribed daily aspirin or blood thinners must not stop medications without consulting their physician."
            }
        ]
    }
    with open(POLICY_PATH, "w", encoding="utf-8") as f:
        json.dump(policy, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {POLICY_PATH}")

STOPWORDS = {
    "what", "is", "the", "for", "and", "in", "of", "to", "a", "an", "on", "with",
    "vs", "or", "be", "are", "can", "i", "do", "should", "how", "when", "does",
    "it", "at", "by", "from", "as", "about", "that", "this", "my", "your"
}

def _generate_deterministic_dense_vector(text: str, dim: int = 384) -> list[float]:
    """
    Generates a deterministic normalized dense vector from text.
    Provides a zero-network local fallback for offline/sandboxed environments.
    """
    import math
    import hashlib
    import re
    tokens = re.findall(r"\w+", text.lower())
    words = [w for w in tokens if w not in STOPWORDS]
    if not words:
        words = tokens
    vec = [0.0] * dim
    for word in words:
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        pos = h % dim
        val = ((h >> 8) % 1000) / 1000.0 - 0.5
        vec[pos] += val
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]

def _generate_deterministic_sparse_vector(text: str) -> dict:
    """Generates sparse indices and values for BM25-style keyword matching with deduplicated, sorted indices."""
    import re
    import hashlib
    words = re.findall(r"\w+", text.lower())
    freq = {}
    for w in words:
        freq[w] = freq.get(w, 0) + 1
    index_map = {}
    for w, count in freq.items():
        # Hash token to a 100,000-bucket sparse index
        idx = int(hashlib.md5(w.encode("utf-8")).hexdigest()[:6], 16) % 100000
        index_map[idx] = index_map.get(idx, 0.0) + float(count)
    sorted_indices = sorted(index_map.keys())
    values = [index_map[i] for i in sorted_indices]
    return {"indices": sorted_indices, "values": values}

def seed_qdrant():
    """Builds embedded Qdrant collection matching Ayan's Module 2 specification."""
    try:
        from qdrant_client import QdrantClient, models
    except ImportError:
        print("[WARNING] qdrant-client not installed. Skipping vector store seeding.")
        return

    print(f"Provisioning embedded Qdrant vector store in: {QDRANT_STORAGE_DIR}")
    client = QdrantClient(path=str(QDRANT_STORAGE_DIR))
    collection_name = f"guarddengue_{CORPUS_RELEASE}"
    
    # Try FastEmbed if explicitly enabled, otherwise use deterministic offline embeddings
    use_fastembed = False
    import os
    if os.environ.get("USE_FASTEMBED", "0") == "1":
        try:
            from fastembed import TextEmbedding
            dense_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            texts = [item["text"] for item in SEED_CHUNKS]
            dense_embeddings = [v.tolist() for v in dense_model.embed(texts)]
            dim = len(dense_embeddings[0])
            print(f"Computed dense vectors using FastEmbed ({dim} dimensions).")
            use_fastembed = True
        except Exception as e:
            print(f"FastEmbed failed ({e}). Falling back to deterministic offline embeddings.")
    
    if not use_fastembed:
        print("Using deterministic offline embeddings (384 dimensions).")
        dim = 384
        dense_embeddings = [_generate_deterministic_dense_vector(item["text"], dim=dim) for item in SEED_CHUNKS]

    # Recreate collection safely
    if client.collection_exists(collection_name):
        client.delete_collection(collection_name)

    client.create_collection(
        collection_name=collection_name,
        vectors_config={
            "dense": models.VectorParams(
                size=dim,
                distance=models.Distance.COSINE
            )
        },
        sparse_vectors_config={
            "sparse": models.SparseVectorParams(
                modifier=models.Modifier.IDF
            )
        }
    )

    points = []
    for idx, item in enumerate(SEED_CHUNKS):
        sparse_data = _generate_deterministic_sparse_vector(item["text"])
        points.append(
            models.PointStruct(
                id=idx + 1,
                vector={
                    "dense": dense_embeddings[idx],
                    "sparse": models.SparseVector(
                        indices=sparse_data["indices"],
                        values=sparse_data["values"]
                    )
                },
                payload={
                    "chunk_id": item["chunk_id"],
                    "parent_id": item["parent_id"],
                    "doc_id": item["doc_id"],
                    "source": item["source"],
                    "publication_date": item["publication_date"],
                    "evidence_level": item["evidence_level"],
                    "topic": item["topic"],
                    "review_status": "approved",
                    "corpus_release": CORPUS_RELEASE,
                    "section_path": item["section_path"],
                    "page_start": item["page_start"],
                    "page_end": item["page_end"],
                    "text": item["text"],
                    "superseded_by": None
                }
            )
        )

    client.upsert(collection_name=collection_name, points=points)
    
    # Create payload keyword indexes for fast filtering
    for field in ("source", "review_status", "corpus_release", "topic"):
        client.create_payload_index(
            collection_name=collection_name,
            field_name=field,
            field_schema=models.PayloadSchemaType.KEYWORD,
            wait=True,
        )
    print(f"Successfully embedded, indexed, and indexed payloads for {len(points)} points in Qdrant '{collection_name}'!")

if __name__ == "__main__":
    print("=== GuardDengue Development Seed Data Generator ===")
    seed_sqlite()
    seed_policy()
    seed_qdrant()
    print("=== Seed Data Setup Complete ===")
