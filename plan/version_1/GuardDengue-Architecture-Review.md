GuardDengue: Architecture
Review and Alternatives
Analysis

Project: A Safety-Aware LLM/SLM Framework for Evidence-Grounded Dengue Health Awareness

Purpose: University research architecture; health education, not diagnosis, prescribing, or autonomous triage.

Review date: 23 September 2026

Executive recommendation

Recommended stack: Docling + structure-aware LlamaIndex nodes + Qdrant dense/sparse retrieval + a clinician-

curated Neo4j knowledge graph + LangGraph orchestration. Use deterministic, versioned safety policies and clinician-

approved response templates for emergency and medication-safety pathways. Add NeMo Guardrails only where it

provides a measured benefit; it is not a replacement for these controls.

The architecture should distinguish two activities:

Offline evidence preparation: acquire permitted sources, preserve document structure, review high-risk extracted

content, assign metadata, and publish a versioned knowledge release.

Online education: screen the request, retrieve eligible evidence, generate a constrained educational response,

verify claims and policies, and either release the verified answer or use a safe fallback.

Neither RAG, a knowledge graph, nor an LLM verifier can guarantee zero medical misinformation. For safety-critical

content, reduce generative freedom rather than relying on a model to correct another model. Treat clinical validation and

ongoing incident monitoring as deployment requirements.

1. Literature grounding and necessary
corrections

Proposed
grounding or
assumption

Architectural interpretation

Proposed
grounding or
assumption
Amugongo et al.
(2025), Retrieval
augmented
generation for large
language models in
healthcare: A
systematic review
[1]

Basu and Huynh
(2026), DOI
10.1186/s12913-
026-14851-1 [2]

Tables should not
be flattened
indiscriminately

Every visual
flowchart must pass
through a VLM

Emergency queries
should be instantly
blocked

NSAIDs, aspirin,
and ibuprofen
should be blocked

WHO material is
public domain

Architectural interpretation

Verified. The review discusses naive, advanced, modular, and
knowledge-graph-augmented RAG, as well as residual errors and
evaluation limitations. It motivates better retrieval and verification, but
does not establish this proposed schema as mandatory or certify this
architecture. Its discussion of approximately 45% concerns responses
not fully supported by retrieved URLs, not a hallucination-reduction
benefit.

Verified publication and relevant review claims. It describes the
input/context/fact-conflicting taxonomy, KG-based verification, and
CoMT. It reports 25-45% hallucination reductions for selected KG
approaches, but uses heterogeneous narrative synthesis rather than
meta-analysis. The exact 45% endpoint was not independently traced
to an original experiment in this review; do not transfer that figure to
GuardDengue.
Sound design principle. Preserve cell coordinates, row/column
headers, spans, units, conditions, and footnotes. Markdown is a useful
presentation format, but is not a lossless representation of every
clinical table.
A VLM is one extraction option, not a correctness guarantee or
universal requirement. Prefer an authoritative machine-readable
equivalent when available. For image-only flowcharts, use VLM-
assisted structured extraction followed by review. A prose description
alone can lose branch logic.
Replace blocking with an immediate safety response. A person
reporting potentially urgent symptoms should receive clear, approved
guidance to obtain medical help, not a refusal or a wait for RAG. This
does not authorize the system to diagnose dengue or assert that the
person is safe.
Block recommendations to use them for suspected dengue, not
their names. The system must be able to explain that these medicines
should be avoided in this context. Do not automatically tell a person to
stop an existing prescribed medicine; route that situation to a clinician.
Publicly accessible does not mean public domain. Record and comply
with each document's actual reuse license, attribution requirements,
and third-party-content exclusions.

The intended scope is general dengue education plus conservative safety escalation. A disclaimer alone does not

prevent diagnostic behavior: the output policy must also prohibit personalized diagnoses, declarations of "no risk," severity

scoring, and unsupervised treatment plans.

What the hallucination taxonomy and CoMT actually support

Basu and Huynh's Box 1 distinguishes input-conflicting output, which contradicts supplied input; context-conflicting

output, meaning internal inconsistency within generated content; and fact-conflicting output, which contradicts

established medical knowledge. The review attributes this taxonomy to earlier work. Test contradictions with retrieved

evidence separately rather than redefining "context-conflicting" to mean only retrieval disagreement.

The original CoMT research concerns hierarchical question-answer chains derived from radiology reports for training/fine-

tuning medical report generation [19]. It is not a demonstration that asking a dengue chatbot to reveal a medical reasoning

chain verifies its answers. Basu and Huynh report a 38% reduction in catastrophic hallucinations for CoMT, but that exact

figure was not independently reproduced from the original study during this review. It should not be combined with the KG

range into a general effectiveness promise.

WHO's dengue fact sheet explicitly advises avoiding NSAIDs such as aspirin and ibuprofen because of bleeding risk, and

seeking immediate care for severe symptoms [18]. It also warns that severe symptoms can occur after the fever subsides.

These support reviewed safety messages, not automated diagnosis or a declaration that someone without a matched

warning is safe.

Evidence contract shared by all modules

Retain the four required metadata fields, but give them controlled semantics:

Field

source

publication_date

evidence_level

topic

Required meaning and validation
Canonical source identifier or URL resolved through an approved source
registry. Do not trust publisher names supplied by a user, model, or
document itself.
Actual publication or revision date, recorded in ISO format. Never
substitute ingestion time. Quarantine missing or ambiguous dates for
editorial resolution rather than inventing them.
A documented, reviewer-assigned classification. Preserve an
authoritative evidence grade when one exists; otherwise explicitly record
that it is ungraded. Publisher prestige is not itself an evidence grade.
One or more controlled labels from the specified 13-category taxonomy.
Multi-label assignment is useful for passages that concern children,
medication safety, and emergency guidance simultaneously.

Topic vocabulary: Dengue basics; Transmission; Symptoms; Prevention; Hydration; Warning signs; Diagnosis; Myths;

Children; Pregnancy; Medication safety; Outbreak awareness; Emergency guidance.

Also retain document_id, document_version, content_hash, chunk_id, page, section_path, source bounding

boxes where available, language, jurisdiction, population, review_status, reviewed_at, review_due,

corpus_release, license, and supersession information. Keep table/figure identifiers and links to their original source

objects.

Apply strict filters to evidence eligibility, not blindly to inferred subject matter. An uncertain topic classifier must not

exclude a relevant warning. Retrieve mandatory medication-safety and warning-sign policy material independently of

ordinary semantic ranking.

Publication recency is not equivalent to validity. An older, still-current guideline can remain eligible; outbreak reports

additionally require geographic and time-window applicability.

2. Module 1: Document parsing and
multimodal ingestion

Best practice

Preserve a canonical structured representation and the original source alongside any text used for retrieval. Use native

DOCX/HTML structure where available rather than rasterizing everything through OCR.

For tables, retain the cell grid, merged headers, units, comparison operators, population qualifiers, captions, and footnotes.

Where a table must be divided for retrieval, repeat the applicable headers and qualifiers and preserve a pointer to the

complete table. Do not treat CSV or Markdown alone as a lossless clinical evidence store.

For diagrams, extract a structured object containing nodes, directed edges, branch labels, conditions, source coordinates,

and ambiguous or unreadable elements. Retain the source image. Have a qualified reviewer approve high-risk clinical

logic before it becomes answerable evidence. VLM output is an extraction hypothesis, not a new medical source.

Alternatives

Latency descriptions below are qualitative. Parsing is normally an offline cost; measure it on the actual corpus and

hardware rather than assuming a universal ranking.

Alternative
and
deployment

Fidelity and safety
advantages

Fidelity and safety
limitations

unstructured:
open-source
local
partitioning;
commercial
hosted
processing
also available
[3]

Broad format support;
typed elements such
as titles, paragraphs,
tables, and images;
element metadata
supports provenance.
High-resolution PDF
processing can infer
table structure and
expose table HTML.

Docling:
open-source
local
execution;
can be
deployed
behind a self-
hosted API
[4]

A unified
DoclingDocument
retains text, tables,
pictures, hierarchy, and
provenance. Strong fit
for keeping canonical
structured objects,
source images, and
human-review artifacts
together. Supports
PDF, DOCX, and
HTML.

Results depend strongly on
document type and partition
strategy. Fast text extraction
is not equivalent to layout-
aware extraction. Title
detection and reading order
can be wrong. Its chunker
can text-split oversized
tables, so clinical tables
need an explicit separate
policy.

OCR, header inference,
merged cells, and reading
order remain fallible. Export
formats are projections of
the document; not all
preserve every attribute. A
default chunk serializer
should not be assumed to
preserve the original table
grid.

Latency and
operational trade-
offs

Fast paths suit clean
digital documents;
layout detection and
OCR add processing
time and
dependencies. Hosted
processing adds
network, service, and
data-governance
considerations.

Model initialization and
OCR/layout inference
cost more than plain
extraction. Local
processing supports
caching and
reproducibility but
needs
model/dependency
management;
hardware affects
throughput.

Alternative
and
deployment

Fidelity and safety
advantages

Fidelity and safety
limitations

Latency and
operational trade-
offs

LlamaParse /
LlamaCloud
Parse:
managed API
with client
libraries [5]

Layout-aware parsing
with Markdown/JSON
outputs and handling of
tables, charts, and
scans. Attractive when
the team wants
managed document-
processing operations.

Accuracy remains
document-dependent;
generative parsing can
misread or introduce
content. An open-source
client does not make the
hosted parser an entirely
local, open-source
processing stack. Review
retention, region, terms, and
reproducibility requirements.

Uploads, service
queues, parser tier,
and API limits affect
completion time and
cost. Reduces local
infrastructure work.
Pin supported parser
versions rather than
depending on an
unversioned "latest"
configuration.

Recommendation: Docling, with reviewed VLM assistance

Use Docling as the default parser, preserving its structured JSON as the canonical extraction artifact and HTML as a

review/display representation for tables.

For difficult diagrams, compare a pinned local Qwen2.5-VL checkpoint against an institution-approved Gemini

multimodal API model on a reviewed diagram set. Local processing gives more control over data movement but requires

suitable compute and checkpoint-license review. An API reduces local serving work but introduces service, retention, and

version-change dependencies. Neither option should publish clinical branches without review.

For a small guideline corpus, manual transcription and independent review of safety-critical flowcharts may be more

dependable and cheaper than automating all diagram interpretation.

Example: preserve tables and figure crops with Docling

This integration example writes extraction artifacts, not an approved clinical knowledge base. Model assets and OCR

dependencies must already be provisioned.

from pathlib import Path

from docling.datamodel.base_models import ConversionStatus, InputFormat

from docling.datamodel.pipeline_options import PdfPipelineOptions

from docling.document_converter import DocumentConverter, PdfFormatOption

options = PdfPipelineOptions()

options.do_ocr = True

options.do_table_structure = True

options.generate_page_images = True

options.generate_picture_images = True

converter = DocumentConverter(

    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}

)

result = converter.convert(Path("approved-guideline.pdf"))

if result.status != ConversionStatus.SUCCESS:

    raise RuntimeError(f"Document requires extraction review: {result.status}")

document = result.document

output = Path("extraction")

output.mkdir(exist_ok=True)

document.save_as_json(output / "document.json")

for index, table in enumerate(document.tables):

    (output / f"table-{index}.html").write_text(

        table.export_to_html(doc=document), encoding="utf-8"

    )

for index, picture in enumerate(document.pictures):

    image = picture.get_image(document)

    if image is None:

        raise RuntimeError(f"Missing source image for picture {index}")

    image.save(output / f"picture-{index}.png")

Keep the original document hash and the table/figure source references in the ingestion manifest. A successful parser

status is not evidence of clinical extraction accuracy.

3. Module 2: Semantic and structure-aware
chunking

Best practice

Chunk around evidence units, not arbitrary text lengths. A useful unit preserves an assertion together with its applicable

population, conditions, negation, warning, and source locator.

Retain document hierarchy and explicit links between a passage and its governing warnings. Use child chunks for precise

retrieval, then expand to a bounded parent section or linked safety passages before generation. Never silently truncate a

critical qualifier to satisfy a token budget.

Token limits still matter: structure-aware chunking does not remove embedding or context-window limits. Oversized units

need a content-aware split, an appropriate structured representation, or editorial handling.

Method alternatives

Method

Title/Markdown
section
chunking

Document-
structure
parent/child
chunking

RAPTOR:
recursive
embedding,
clustering, and
abstractive
summarization
[8]

Evidence-fidelity
and safety
advantages

Transparent,
deterministic
boundaries;
straightforward
source attribution;
retains recognizable
headings when
configured
appropriately. Good
baseline for clean
guideline prose.
Retains original
wording at each
retrieval level. Small
matches can be
expanded to their
source section and
associated warnings
without inventing a
summary.
Useful for broad,
cross-document or
thematic questions
over large corpora.
Hierarchical
summaries can
improve access to
information at
different abstraction
levels.

Limitations

Latency and cost

Depends on correct heading
extraction. A warning under a
separate heading can still
become detached. Very large
sections need special handling;
Markdown tables can lose rich
table semantics.

Low preprocessing
cost; no
summarization
model required.
Ordinary retrieval
latency.

Parent expansion can
reintroduce excessive context.
Parent/child links alone do not
encode every clinical
dependency; explicit warning
and qualifier links are still
needed.

Modest
indexing/storage
overhead.
Expansion and
reranking add
bounded retrieval
work.

Not merely a structure-
preserving splitter. Generated
summaries may omit negation,
populations, exceptions, and
numeric qualifiers, or combine
incompatible source versions.
Summaries must not become
the sole evidence for medication
or emergency guidance.

Higher offline cost
from clustering
and repeated
summarization.
Query cost
depends on tree
traversal and
retrieval design; it
is not universally
faster or slower.

RAPTOR recommendation: keep it out of the initial safety-critical answer path. If evaluated later, use its summaries to

locate original evidence, then retrieve and verify the underlying source passages.

Library alternatives

Library

Strengths for
GuardDengue

Limitations and safety
considerations

Deployment and
latency

LangChain
text
splitters [6]

LlamaIndex
node
parsers
and nodes
[7]

Lightweight, composable
splitters for Markdown,
HTML, and text.
MarkdownHeaderTextSplitter
exposes header metadata;
strip_headers=False
preserves headings in
content.

Parent/child relationships,
mandatory warning
retrieval, and clinical
atomicity need application
logic. A second recursive
character split can undo the
benefit of section
boundaries.

Nodes support metadata
and
source/parent/adjacency
relationships; Markdown,
semantic, sentence-window,
and hierarchical parsing
options are available.
Convenient for retrieval plus
context expansion.

HierarchicalNodeParser is
not RAPTOR and its default
size-based hierarchy is not
automatically clinically
structure-aware. Auto-
merging must remain
bounded. No parser
guarantees preservation of
warnings or numeric
attributes.

Open-source and
local. Deterministic
splitting needs no
model API;
embedding-based
strategies add local
or API inference
cost.
Open-source and
local. Deterministic
parsers are
inexpensive;
semantic splitting
requires
embeddings.
Model-backed
components can
use local models or
APIs.

Recommendation: structure-aware LlamaIndex nodes,
without RAPTOR initially

Use Docling structure as the source of boundaries, then represent the approved evidence units as LlamaIndex nodes.

Use MarkdownNodeParser for already-reviewed prose sections with reliable headings. Keep tables and flowcharts on

dedicated structured paths.

For clinical safety, add explicit relationships such as governed_by_warning, requires_qualifier,

parent_section, and superseded_by. These are application relationships, not capabilities a text splitter creates

automatically.

Example: parse a reviewed prose section with inherited
metadata

The metadata file below must come from the reviewed source registry. This is a basic integration example; the production

ingestion boundary should additionally enforce the complete schema and controlled topic/evidence vocabularies.

import json

from datetime import date

from pathlib import Path

from llama_index.core import Document

from llama_index.core.node_parser import MarkdownNodeParser

metadata = json.loads(

    Path("reviewed-section.metadata.json").read_text(encoding="utf-8")

)

required = {"source", "publication_date", "evidence_level", "topic"}

if any(not metadata.get(key) for key in required):

    raise ValueError("Missing required evidence metadata")

if metadata.get("review_status") != "approved":

    raise ValueError("Unreviewed section cannot enter the answerable index")

date.fromisoformat(metadata["publication_date"])

section = Document(

    text=Path("reviewed-prose-section.md").read_text(encoding="utf-8"),

    metadata=metadata,

)

parser = MarkdownNodeParser.from_defaults(

    include_metadata=True,

    include_prev_next_rel=True,

)

nodes = parser.get_nodes_from_documents([section])

The resulting nodes still need source locators, stable identifiers, token-budget checks, and explicit warning/qualifier links

before publication. Do not run a generic text splitter over the canonical table objects.

4. Module 3: Dual indexing and hybrid
retrieval

Best practice

Separate three functions:

1. Dense retrieval finds semantically related passages.

2. Sparse/lexical retrieval preserves exact matches for medicine names, acronyms, terminology, and numeric

expressions.

3. A curated knowledge graph and policy engine represent reviewed relationships and enforce applicable

constraints.

Dense plus sparse retrieval is the usual meaning of hybrid search here. Adding a graph is an additional evidence and

policy layer; it does not by itself provide lexical retrieval.

Apply eligibility filters to every retrieval branch, fuse results, rerank, deduplicate, and expand necessary source context.

Keep an immutable corpus-release identifier shared by the vector index, graph, source registry, and safety policies.

Eligibility is not recall: a strict metadata predicate can exclude ineligible evidence while approximate nearest-neighbor

search still misses relevant eligible evidence. Fusion cannot recover a passage absent from all candidate sets. Compare

filtered recall against an exact-search baseline, especially under highly selective filters.

Vector-store alternatives

None of these stores improves extraction fidelity after ingestion. Their safety contribution is preserving metadata, enforcing

eligibility, and reliably returning the relevant eligible evidence.

Store and
deployment

pgvector
with
PostgreSQL:
open-source
local/server
deployment;
managed
PostgreSQL
options [9]

Qdrant:
open-source
self-hosted
server;
embedded
local
development
mode;
managed
cloud [10]

Metadata filtering
and strengths
Strong SQL filtering,
relational joins,
transactions,
constraints, and
row-level security.
Attractive if the
institution already
operates
PostgreSQL.
PostgreSQL full-text
search can supply
the lexical branch.
Dedicated payload
indexes and filtered
vector search;
dense and sparse
vectors plus fusion
through its query
API. Convenient fit
for
topic/source/release
filters and a multi-
stage retrieval
pipeline.

Limitations and clinical-safety
implications

Latency and
operations

Approximate index scans with
filtering require care: too few
eligible candidates can be
returned. Use appropriate indexes,
query plans, iterative scans where
supported, or exact search for
small eligible subsets.
Sparse/dense fusion is
application/query logic rather than
a single universal default.

Often the simplest
operational footprint
for a modest corpus
already stored in
PostgreSQL. Query
planning, selectivity,
index choice, and
concurrency
determine
performance.

Payload indexes must be designed
for actual filters. Restrictive filter
combinations can still reduce
approximate-search recall.
Payload indexes have no effect in
Python local mode, so it is not a
substitute for server-index
performance evaluation. Schema
and transactional coordination with
a separate graph remain
application responsibilities.

Good feature fit for
an independently
deployed retrieval
service. More
infrastructure than
a PostgreSQL-only
design; actual
latency depends on
filter selectivity,
vector size, corpus,
and hardware.

Store and
deployment
Milvus:
open-source
local Lite,
standalone,
and
distributed
options;
managed
options such
as Zilliz
Cloud [11]

Metadata filtering
and strengths

Limitations and clinical-safety
implications

Latency and
operations

Scalar filtering,
scalar indexes,
multi-vector/hybrid
search, built-in
BM25 sparse
retrieval, and
scaling options for
large collections.

More configuration and operational
choices. Standard versus iterative
filtering, index behavior, and read
consistency require workload-
specific evaluation. Distribution
does not guarantee better
relevance or safer answers.

Attractive when
scale or throughput
justifies it. A server
deployment
typically adds more
operational
complexity than
needed for a small,
curated dengue-
guideline corpus.

Recommendation: Qdrant for a dedicated research retrieval service. If the project already relies on PostgreSQL and the

corpus is small, pgvector is a strong simpler alternative; do not introduce Qdrant solely on an unmeasured claim that it

is faster.

Graph alternatives

Alternative
and
deployment

Evidence-fidelity
and safety
advantages

Limitations

Latency and
operations

Neo4j: self-
hosted
database;
managed Aura
service [12]

Explicit property
graph, parameterized
Cypher, relationship
provenance, and
mature inspection
tooling. Well suited to
reviewing drug
classes, population
conditions, and
source-backed safety
rules.

Kuzu:
embedded
local graph
database [13]

Historically attractive
for a reproducible,
embedded research
graph with no
separate server and a
Cypher-like query
interface.

A graph stores assertions;
it does not make them
true. LLM-extracted edges
require approval.
Constraints do not replace
clinical validation. Edition
and deployment
capabilities differ.

Indexed, bounded
traversals can avoid
model calls. A separate
database adds
deployment and release-
coordination work.

The original upstream
repository is archived,
verified as of 23
September 2026. Its
README archival
announcement is dated 10
October 2025. Do not
select it as an actively
maintained dependency for
a new safety-critical
deployment.

Minimal network
overhead in-process;
potentially useful for
frozen reproducibility
experiments. Lack of
ongoing upstream
maintenance outweighs
that convenience for the
proposed maintained
service.

Alternative
and
deployment

Evidence-fidelity
and safety
advantages

Limitations

Latency and
operations

Microsoft
GraphRAG:
open-source
indexing/query
pipeline using
configurable
models [14]

Extracted entity
relationships and
community
summaries can help
corpus exploration
and broad questions.
Can provide a useful
research comparison
against ordinary
retrieval.

Not a graph database
equivalent to Neo4j or
Kuzu. Model-extracted
relationships and
summaries are
probabilistic. They must
not become an
authoritative
contraindication registry
without review.

Potentially substantial
offline
extraction/summarization
cost and additional
query-time model calls,
depending on search
mode. More machinery
than necessary for a
small deterministic
safety graph.

Recommendation: Neo4j for reviewed relationships; code for
enforcement

Use Neo4j as the inspectable evidence graph, but compile the approved safety policy into a versioned local rules artifact

available even if the graph server is unavailable.

Prefer a scoped relation such as:

(Aspirin)-[:MEMBER_OF]->(NSAIDs)

(NSAIDs)-[:AVOID_IN {

    context: "suspected_dengue",

    source_chunk_id: "...",

    corpus_release: "...",

    review_status: "approved"

}]->(DengueContext)

This is a policy-modeling example, not an assertion that one unqualified Contraindicates edge captures every

prescribing situation. Retain source wording, scope, provenance, and validity. Normalize aliases, brands, spelling variants,

and supported-language names through a reviewed terminology registry.

Absence of a graph edge does not establish safety. Unknown medicines or unsupported clinical situations must not

produce a permissive recommendation. Do not execute model-generated Cypher against the safety graph.

Example: filtered dense/sparse retrieval with Qdrant

Assumptions: a Qdrant server is running; collection guarddengue has named dense and sparse vector configurations;

ingestion used compatible embedding models; and metadata is validated. Provision payload indexes once, preferably

before ingesting vectors so filter-aware indexing can be built appropriately.

from qdrant_client import QdrantClient, models

client = QdrantClient(url="http://localhost:6333")

for field in ("source", "review_status", "corpus_release", "topic"):

    client.create_payload_index(

        collection_name="guarddengue",

        field_name=field,

        field_schema=models.PayloadSchemaType.KEYWORD,

        wait=True,

    )

def retrieve(dense, sparse, source_ids, release):

    if not source_ids or not release:

        raise ValueError("An approved source allowlist and release are required")

    eligible = models.Filter(must=[

        models.FieldCondition(

            key="source", match=models.MatchAny(any=source_ids)

        ),

        models.FieldCondition(

            key="review_status", match=models.MatchValue(value="approved")

        ),

        models.FieldCondition(

            key="corpus_release", match=models.MatchValue(value=release)

        ),

    ])

    return client.query_points(

        collection_name="guarddengue",

        prefetch=[

            models.Prefetch(

                query=dense, using="dense", filter=eligible, limit=30

            ),

            models.Prefetch(

                query=sparse, using="sparse", filter=eligible, limit=30

            ),

        ],

        query=models.FusionQuery(fusion=models.Fusion.RRF),

        query_filter=eligible,

        limit=8,

        with_payload=True,

    ).points

Here dense is a dense query vector and sparse is a models.SparseVector, produced using the same respective

encoders as ingestion. source_ids and release come from trusted application configuration, not user or model output.

The example limits are tuning parameters, not clinically validated settings.

Apply optional topic filters only after recall evaluation. Retrieve mandatory safety rules separately so a topic error or a low

similarity rank cannot suppress them. Add jurisdiction, population, active/superseded status, and time-window eligibility as

required by the source registry.

Example: bounded, parameterized Neo4j policy lookup

import os

from neo4j import GraphDatabase

with GraphDatabase.driver(

    os.environ["NEO4J_URI"],

    auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),

) as driver:

    records, _, _ = driver.execute_query(

        """

        MATCH (d:Drug {id: $drug_id})-[:MEMBER_OF]->(c:DrugClass)

        MATCH (c)-[r:AVOID_IN]->(:ClinicalContext {id: $context})

        WHERE r.review_status = 'approved'

          AND r.corpus_release = $release

        RETURN c.id AS drug_class, r.source_chunk_id AS evidence

        """,

        drug_id="aspirin",

        context="suspected_dengue",

        release=os.environ["GUARDDENGUE_CORPUS_RELEASE"],

        database_="neo4j",

        routing_="r",

    )

The lookup illustrates one reviewed relation, not a complete medication-safety classifier. A missing match, graph failure, or

unresolved alias must not authorize medication use. Read routing is not an authorization boundary; use appropriately

restricted credentials and server permissions.

5. Module 4: Orchestration and safety
guardrails

Best practice

Implement a bounded, auditable verification workflow, not an unconstrained agent instructed to think like a physician.

The CoMT paper supports studying structured medical reasoning, but the workflow proposed here is an engineering

adaptation, not a reproduction of its radiology-report training method.

Store concise structured outputs such as claim, source_chunk_id, source_span, policy_check, and verdict.

Free-form model reasoning is neither evidence nor a safety certificate.

The online flow should be:

User message and relevant conversation context

  -> input normalization and safety screening

     -> reported/possible urgent concern: approved escalation response

     -> medication safety: reviewed policy/template pathway

     -> educational request:

          eligibility-filtered dense + sparse retrieval

          -> rerank + bounded source/qualifier expansion

          -> evidence sufficiency and conflict gate

          -> constrained draft

          -> deterministic policy + structured claim verification

             -> pass: release the exact verified output

             -> repairable grounding issue: one bounded revision

             -> reject, unresolved, timeout, or unavailable evidence:

                  explicit safe fallback

Regex and terminology rules are useful for known high-risk patterns, but are not a complete emergency detector. Semantic

routing is model-based and should not be described as clinically deterministic merely because its inference settings are

fixed. Evaluate negation, misspellings, language variation, quoted examples, hypothetical questions, and conversational

context.

Do not interpret the absence of a matched warning as proof that a user is safe. When symptoms may be urgent, provide

an approved escalation message without waiting for generation. Do not let generic moderation hide necessary emergency

guidance.

Alternatives

Framework
and
deployment

Advantages for
evidence fidelity and
safety

Limitations

Latency and
operations

Framework
and
deployment

LangGraph:
open-source
local/self-
hosted
orchestration;
managed
deployment
options [15]

Advantages for
evidence fidelity and
safety
Explicit state, conditional
edges, cycles,
checkpoints, and
controlled handoffs.
Makes screening,
retrieval, verification,
revision, and abstention
visible as separate steps.
Works with local models
or model APIs.

Limitations

It orchestrates policy but
does not supply a validated
clinical policy. Unbounded
cycles, unsafe callbacks,
exposed streaming, or poorly
isolated conversation state
can defeat the design.
Checkpoints and traces may
contain sensitive data.

LlamaIndex
Workflows:
open-source
event-driven
Python
workflows;
local models
or APIs [16]

NeMo
Guardrails:
open-source
library/self-
hosted
service; local
or API-
backed
models and
checks [17]

Typed events and steps
support branching, loops,
concurrency, and human
review. Good fit if the
team already uses
LlamaIndex for evidence
ingestion and retrieval.

Not restricted to DAGs, but
safety invariants still need
application enforcement.
Dynamic event dispatch can
make execution less obvious
if used without disciplined
contracts.

Dedicated input,
retrieval, dialog,
execution, and output
rails; Colang flows and
custom Python actions.
Useful as an additional
policy layer.

Not a substitute for a clinical
workflow engine or verified
evidence. LLM self-checking
remains fallible and needs
evaluation. Generic content-
safety models do not reliably
detect dengue-specific
unsafe advice.

Latency and
operations

Framework
overhead is
generally secondary
to inference,
retrieval, and
network calls.
Explicit limits make
worst-case model-
call counts easier to
control.
Similar dominant
costs: models and
external services.
Async steps can
overlap independent
work; integration
may be simpler in an
all-LlamaIndex
stack.
Deterministic checks
are lightweight;
model-based rails
add inference calls
and latency.
Additional
configuration/runtime
complexity can
duplicate existing
orchestration.

Recommendation: LangGraph plus deterministic policies

Choose LangGraph for the primary control flow. Keep clinical policy enforcement in ordinary, versioned Python code and

reviewed templates. Use LlamaIndex only for the evidence components that are useful; avoid running two orchestration

engines for the same request.

Add NeMo Guardrails selectively for a clearly identified need, such as a reusable injection-detection or output-policy rail.

Its self-check prompts are a starting point, not validated medical safeguards.

Required verification behavior

Required behavior

Every medical factual claim must map to an eligible source passage or a
reviewed structured source object. Verify support, not merely the existence
of a citation.
Compare numbers, units, inequality signs, populations, table coordinates,
and conditions against canonical evidence. Do not rely solely on an LLM's
similarity judgment.

Check

Evidence
support

Numeric and
structural
fidelity

Check

Medication
policy

Diagnosis and
triage
boundary
Contradictions
and
uncertainty
Input and
retrieval
integrity

Failure
handling

Output
release

Required behavior
Reject recommendations to use blocked medicine classes in the applicable
dengue context. Permit explanations of avoidance. Route existing-
prescription questions conservatively to professional review.
Reject personalized diagnostic conclusions, unsupported severity
classifications, and reassurance that symptoms are harmless. A source
citation does not make such personalization appropriate.
Do not silently choose between conflicting guidelines. Resolve through
documented source applicability/precedence, or acknowledge the
unresolved conflict and abstain from the disputed advice.
Treat user messages and retrieved documents as data, not instructions.
Keep tool permissions narrow and prevent retrieved content from rewriting
policies.
Use explicit, approved fallback messaging and privacy-preserving error
reporting. Never replace missing evidence with model memory. Keep
emergency templates available locally.
Do not stream unverified draft tokens. Publish exactly the verified response;
a later generative rewrite or translation requires verification again.

For a small SLM, narrower outputs, reviewed templates, and concise evidence are particularly important. Model size alone

is not a dependable measure of clinical safety; choose the generator and any verifier through task-specific evaluation.

Example: bounded LangGraph verification loop

This is workflow wiring, not a production clinical guardrail implementation. The supplied nodes are application callbacks

that must implement the contracts above. screen returns urgent, education, medication, or uncertain; verify

returns pass, revise, or reject. The template pathways must return reviewed content, not unrestricted model

completions.

from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

class State(TypedDict):

    question: str

    route: Literal["urgent", "education", "medication", "uncertain"]

    attempts: int

    evidence: list[dict]

    evidence_ok: bool

    draft: str

    verdict: Literal["pass", "revise", "reject"]

    answer: str

def build_workflow(nodes):

    graph = StateGraph(State)

    for name in (

        "screen", "urgent", "medication", "retrieve",

        "verify", "publish", "abstain"

    ):

        graph.add_node(name, nodes[name])

    def draft(state):

        update = nodes["draft"](state)

        return {**update, "attempts": state["attempts"] + 1}

    def after_verification(state):

        if state["verdict"] == "pass":

            return "publish"

        if state["verdict"] == "revise" and state["attempts"] < 2:

            return "draft"

        return "abstain"

    graph.add_node("draft", draft)

    graph.add_edge(START, "screen")

    graph.add_conditional_edges("screen", lambda state: state["route"], {

        "urgent": "urgent", "medication": "medication",

        "education": "retrieve", "uncertain": "abstain",

    })

    graph.add_conditional_edges(

        "retrieve",

        lambda state: "draft" if state["evidence_ok"] else "abstain",

        {"draft": "draft", "abstain": "abstain"},

    )

    graph.add_edge("draft", "verify")

    graph.add_conditional_edges("verify", after_verification, {

        "publish": "publish", "draft": "draft", "abstain": "abstain"

    })

    for terminal in ("urgent", "medication", "publish", "abstain"):

        graph.add_edge(terminal, END)

    return graph.compile()

Initialize attempts to zero in trusted application code. Screening must check emergency concerns before selecting a

medication-only response. The retrieval callback must set evidence_ok from evidence sufficiency, applicability, and

conflict checks, not merely from a nonempty result. Deployment code needs explicit deadlines, dependency-failure

handling, and safe fallbacks. A second draft is not appropriate for a critical policy violation: return reject, not revise.

6. Clinical evaluation and release
requirements

Architecture alone does not establish safety. Before exposing GuardDengue to users, define a clinician-reviewed

evaluation set and release gates that reflect the actual supported languages and populations.

Evaluation
area

Extraction

Retrieval

Grounding

Medication
safety
Emergency
handling

Scope control

Reliability and
latency

Accessibility
and
comprehension

Governance

What to measure or inspect

Exact preservation of critical values, units, operators, table header
associations, footnotes, and flowchart branches. Review all safety-critical
source objects in a small initial corpus.
Recall of required evidence under the real metadata filters, including safety
passages that are not the top semantic match. Include empty-result and
overly restrictive-filter cases.
Claim-level source support, citation accuracy, omission of necessary
qualifiers, and handling of contradictory or insufficient evidence.
Unsafe recommendation rate; aliases and combination products; negation;
requests for substitutes; existing prescriptions; adversarial instructions.
Missed escalation and inappropriate reassurance, as well as unnecessary
escalation. Include hypothetical, quoted, multilingual, and multi-turn cases.
Attempts to obtain a diagnosis, interpret an individual's laboratory results,
receive personalized dosing, or obtain a severity score.
Tail latency for both the template and education paths; model/API outages;
unavailable indexes; stale releases; graph/vector version mismatch;
cancellation and deadline behavior.

Readability and comprehension in the target language, preserving medical
meaning during simplification and translation.

Named clinical owner, source-update process, source/license register,
change review, incident reporting, rollback, and privacy controls.

Report results with denominators and uncertainty intervals. Zero observed failures on a test set is not proof of zero real-

world risk. Do not promise a percentage hallucination reduction before a reproducible GuardDengue evaluation.

Prefer an initially small, fully reviewed knowledge base over a large, weakly curated collection. Disable unsupported

languages or capabilities explicitly rather than allowing the model to improvise.

7. Final recommended technology stack

Layer

Source
acquisition
and
governance

Recommendation

Reason

Approved source registry, original files,
content hashes, license records, clinician-
owned release process

Establishes what counts as
eligible evidence and makes
changes traceable.

Parsing

Docling

Table storage

Diagram
interpretation

Canonical structured table objects plus
HTML review views and original source
crops
VLM-assisted structured extraction, with
manual review; local Qwen2.5-VL or
approved Gemini API as evaluated
candidates

Chunking

Docling structure + LlamaIndex nodes,
deterministic section/parent-child strategy

Retrieval

Knowledge
graph
Runtime
safety
policies

Qdrant dense + sparse search, payload
indexes, eligibility filters, bounded
reranking/context expansion

Neo4j, populated from reviewed assertions

Versioned local Python rules and approved
templates

Orchestration LangGraph

Additional
guardrails

NeMo Guardrails only where justified by
evaluation

Generation

Evaluated local SLM/LLM or institution-
approved API; constrained to supplied
evidence

Initially
exclude

RAPTOR summaries as clinical evidence;
unreviewed GraphRAG safety edges;
autonomous diagnosis, dosing, or severity
scoring

Local execution and a rich
canonical document
representation.
Preserves attributes that
Markdown or plain text can
lose.

Preserves branch logic without
treating model interpretation
as ground truth.

Keeps original evidence and
provenance; avoids
summarization as the safety
foundation.

Direct support for the intended
filtered hybrid retrieval design.

Inspectable relationships with
provenance and scope.
Critical constraints do not
depend on vector similarity or
graph availability.
Explicit routes, bounded
verification/revision, controlled
publication, and failure paths.
Useful supplementary controls
without duplicating the core
safety design.
Model choice follows
measured task performance,
privacy, cost, and serving
constraints.

Avoids unnecessary
probabilistic layers and out-of-
scope clinical behavior.

Simpler deployment option: if the institution already operates PostgreSQL and the corpus is modest, use PostgreSQL +

pgvector + relational policy tables initially. A graph database is useful for inspectability and richer relationships, but is

not inherently required to enforce a small set of reviewed medication-safety rules.

References and implementation
documentation

These sources distinguish research motivation from library capabilities. Product documentation describes features, not

clinical validation.

1. Amugongo LM, Mascheroni P, Brooks S, Doering S, Seidel J. Retrieval augmented generation for large language

models in healthcare: A systematic review. PLOS Digital Health. 2025;4(6):e0000877.

https://doi.org/10.1371/journal.pdig.0000877 (https://doi.org/10.1371/journal.pdig.0000877)

2. Basu S, Huynh B. Mitigating hallucinations in healthcare AI: a systematic review of evidence-based strategies.

BMC Health Services Research. 2026;26:1115. Published 6 June 2026. Publisher article

(https://link.springer.com/article/10.1186/s12913-026-14851-1); DOI (https://doi.org/10.1186/s12913-026-14851-1).

Relevant sections include Box 1, knowledge graphs, self-reflection/verification, and limitations.

3. Unstructured: partitioning (https://docs.unstructured.io/open-source/core-functionality/partitioning) and chunking

(https://docs.unstructured.io/open-source/core-functionality/chunking).

4. Docling: document model (https://docling-project.github.io/docling/concepts/docling_document/), chunking

(https://docling-project.github.io/docling/concepts/chunking/), figure export example (https://github.com/docling-

project/docling/blob/main/docs/examples/export_figures.py), and table export example (https://github.com/docling-

project/docling/blob/main/docs/examples/export_tables.py).

5. LlamaCloud Parse: overview and API examples (https://developers.llamaindex.ai/llamaparse/parse/).

6. LangChain: Markdown header splitting

(https://docs.langchain.com/oss/python/integrations/splitters/markdown_header_metadata_splitter).

7. LlamaIndex: node parsers

(https://developers.llamaindex.ai/python/framework/module_guides/loading/node_parsers/modules/) and nodes

and relationships

(https://developers.llamaindex.ai/python/framework/module_guides/loading/documents_and_nodes/usage_nodes/).

8. Sarthi et al. RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval. ICLR 2024. Paper

(https://arxiv.org/abs/2401.18059); implementation (https://github.com/parthsarthi03/raptor).

9. pgvector: official repository and filtering guidance (https://github.com/pgvector/pgvector).

10. Qdrant: filtering (https://qdrant.tech/documentation/concepts/filtering/), indexing

(https://qdrant.tech/documentation/concepts/indexing/), and hybrid queries

(https://qdrant.tech/documentation/concepts/hybrid-queries/).

11. Milvus: filtered search (https://milvus.io/docs/filtered-search.md) and multi-vector hybrid search

(https://milvus.io/docs/multi-vector-search.md).

12. Neo4j: Python driver documentation (https://neo4j.com/docs/python-manual/current/) and Cypher manual

(https://neo4j.com/docs/cypher-manual/current/).

13. Kuzu: archived upstream repository (https://github.com/kuzudb/kuzu) and README archival announcement

(https://github.com/kuzudb/kuzu/blob/06890e1ac6bd31216f916526b933afc2a7802ec1/README.md).

14. Microsoft GraphRAG: official documentation (https://microsoft.github.io/graphrag/).

15. LangGraph: workflows and agents (https://docs.langchain.com/oss/python/langgraph/workflows-agents) and Graph

API (https://docs.langchain.com/oss/python/langgraph/graph-api).

16. LlamaIndex: Workflows (https://developers.llamaindex.ai/python/llamaagents/workflows/).

17. NVIDIA NeMo Guardrails: overview (https://docs.nvidia.com/nemo/guardrails/latest/index.html) and self-check

limitations/configuration (https://docs.nvidia.com/nemo/guardrails/latest/configure-guardrails/guardrail-catalog/self-

check.html).

18. WHO: Dengue (https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue), dated 21 August

2025; integrated arboviral clinical-management guideline (https://www.who.int/publications/i/item/9789240111110).

Use the applicable authoritative guidance and verify each source's publication/revision date before ingestion.

19. Jiang et al. Original CoMT medical report-generation research: paper (https://arxiv.org/abs/2406.11451) and full text

(https://arxiv.org/html/2406.11451). The task is radiology-report generation, not dengue-awareness conversation.

20. WHO: website terms of use (https://www.who.int/about/policies/terms-of-use) and publishing copyright/licensing

policy (https://www.who.int/about/policies/publishing/copyright). Check each asset's actual license.

Implementation note: The snippets demonstrate library integration and control flow, not a validated medical application.

Pin package/model versions and verify the snippets against those versions before incorporating them into the research

implementation.

