# GuardDengue Phase 1 — Full Pipeline Walkthrough

> **Notebook:** `pipline.ipynb`  
> **Purpose:** Build a safety-first, audit-traceable clinical knowledge pipeline for dengue-related guideline documents. Phase 1 covers document ingestion, structured extraction, parent-child chunking, human-in-the-loop (HITL) governance, vector indexing (Qdrant), knowledge-graph loading (Neo4j optional), medication safety lookup, and cross-store verification.

---

## Cell 1 — Environment & Library Version Check

### Cell Summary
This is the pipeline's first executable cell. It prints the Python interpreter version and checks whether the four core document-handling libraries (`docling`, `pypdf`, `python-docx`, `python-pptx`) are installed, displaying each package's version or a "not installed" message.

### Code Explanation

```python
import sys
from importlib.metadata import PackageNotFoundError, version
```

- `sys.version` gives the full Python version string including the build tag and architecture.
- `importlib.metadata.version()` reads package metadata from the environment without importing the package, so it's safe and fast.

```python
packages = ["docling", "pypdf", "python-docx", "python-pptx"]
for package in packages:
    try:
        print(f"{package}: {version(package)}")
    except PackageNotFoundError:
        print(f"{package}: not installed")
```

Each package is probed in a `try/except` block so the cell does not crash if any library is absent; it prints a human-readable "not installed" message instead. This acts as a lightweight pre-flight check before the heavier ingestion cells run.

**Runtime assumption:** The kernel uses Python 3.12 and all four libraries are pre-installed in the Conda environment (`d1`).

---

## Cell 2 — Core Library Imports

### Cell Summary
Imports every library required by the full Phase 1 pipeline in one place: Docling (PDF parsing), Docling-core types (structural elements), `python-docx`, `python-pptx`, `pypdf`, and Python standard-library modules (`os`, `sqlite3`, `json`, `re`, `uuid`, `hashlib`, `pathlib`, `datetime`). A success message is printed at the end.

### Code Explanation

**Docling imports:**
```python
from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
```
- `ConversionStatus` — enum used later to check whether PDF extraction succeeded (`SUCCESS`) or failed.
- `InputFormat` — tells `DocumentConverter` which format to expect; here, `InputFormat.PDF`.
- `PdfPipelineOptions` — a configuration object that enables OCR, table structure detection, page images, and picture images.
- `DocumentConverter` / `PdfFormatOption` — the main Docling entry point; `PdfFormatOption` wraps pipeline options and passes them to the converter.

**Docling-core structural types:**
```python
from docling_core.types.doc import (
    DoclingDocument, TextItem, ListItem, TableItem, PictureItem,
    ListGroup, SectionHeaderItem, TitleItem,
)
```
These are the data-model building blocks. The pipeline uses `isinstance()` checks against these classes to route each document element to the correct handler (`prose`, `table`, `figure`). Critically, `ListItem` subclasses `TextItem` in Docling, so it must always be checked **before** `TextItem` to avoid list items being silently merged into prose blobs.

**Standard library:**
- `sqlite3` — persistent parent/child chunk store.
- `json` — saves/loads Docling JSON, manifest files, and policy artifacts.
- `re` — whitespace normalisation and drug-alias regex matching.
- `uuid` — deterministic `uuid5` chunk IDs anchored to content.
- `hashlib` — `sha256` for document-level and chunk-level content hashes.
- `pathlib.Path` — cross-platform path handling.
- `datetime` / `timezone` — UTC ISO-8601 timestamps for audit events.

---

## Cell 3 — Configuration: Directories, Corpus Release, and Source Registry

### Cell Summary
Establishes all top-level constants for the pipeline: the documents directory, the `CORPUS_RELEASE` tag, controlled vocabulary sets (`TOPIC_VOCAB`, `EVIDENCE_LEVEL_VOCAB`), a registry validation function, and the authoritative `SOURCE_REGISTRY` dict mapping each PDF filename to its clinical metadata. At the end, every registry entry is validated and an auto-quarantine rule fires for any document whose `publication_date` is `None`.

### Code Explanation

**Directory setup:**
```python
DOCS_DIR = Path("./my_dengue_docs")
DOCS_DIR.mkdir(exist_ok=True)
```
Creates `my_dengue_docs/` if it doesn't exist. All source PDFs live here.

**Corpus release tag:**
```python
CORPUS_RELEASE = os.environ.get("GUARDDENGUE_CORPUS_RELEASE", "v0.1-dev")
```
A single authoritative string tags every chunk, Qdrant point, and policy rule with the pipeline run version. Can be overridden via environment variable for CI/staging environments, ensuring test and production releases never mix.

**Controlled vocabularies:**
```python
TOPIC_VOCAB = frozenset({...})
EVIDENCE_LEVEL_VOCAB = frozenset({"high", "moderate", "low", "very_low", "ungraded"})
```
`TOPIC_VOCAB` lists the 13 allowed clinical topic labels. `EVIDENCE_LEVEL_VOCAB` contains only GRADE-style certainty levels — document types like `"guideline"` or `"rct"` are explicitly disallowed here (they belong in a separate field), and the validator's error message explains this.

**`validate_registry_entry(filename, meta)`:**
This function enforces four rules on every entry before the pipeline runs:
1. `source` must be non-empty (the canonical URL for the document).
2. `topic` must contain at least one label, and every label must be in `TOPIC_VOCAB`.
3. `evidence_level` must be in `EVIDENCE_LEVEL_VOCAB`.
4. `publication_date`: if present it must be a valid ISO date (`date.fromisoformat()`); if absent, `review_status` is auto-set to `"quarantined"` and a `[QUARANTINE]` message is printed.

**`SOURCE_REGISTRY`:**
Three documents are registered:

| Key (filename) | `doc_id` | `publication_date` | `review_status` |
|---|---|---|---|
| `National Guidelines … Dengue Fever.pdf` | `ncvbdc_dengue_guideline_2023` | `None` | `quarantined` |
| `WHO guidelines … arboviral diseases.pdf` | `who_arboviral_guideline_2025` | `2025-07-04` | `pending_review` |
| `Laboratory testing … interim guidance.pdf` | `who_dengue_lab_guidance_2025` | `2025-04-28` | `pending_review` |

The NCVBDC document has no confirmed `publication_date`, so it is auto-quarantined; it will never enter the Qdrant index until a reviewer confirms the date and lifts the quarantine.

**Validation loop:**
```python
for _fname, _meta in SOURCE_REGISTRY.items():
    validate_registry_entry(_fname, _meta)
```
Runs at import/definition time so a misconfigured entry raises immediately, before any expensive PDF parsing begins.

---

## Cell 4 — List Files in `my_dengue_docs/`

### Cell Summary
A simple directory listing cell that prints the `repr()` of every filename in `DOCS_DIR`. Its purpose is to confirm that the PDFs are physically present and that their filenames exactly match the keys in `SOURCE_REGISTRY`.

### Code Explanation
```python
for file_path in sorted(DOCS_DIR.iterdir()):
    if file_path.is_file():
        print(repr(file_path.name))
```
Using `repr()` shows escape characters or hidden whitespace in filenames, which is important because `SOURCE_REGISTRY` performs exact string matching. The expected output lists all three PDFs sorted alphabetically.

---

## Cell 5 — Document Discovery and Registry Matching

### Cell Summary
Discovers all supported documents in `DOCS_DIR`, validates that every discovered file has a corresponding entry in `SOURCE_REGISTRY` (raising `KeyError` if not), and builds the `registered_documents` list that all subsequent cells iterate over.

### Code Explanation

```python
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".md"}
doc_paths = sorted(
    path for path in DOCS_DIR.iterdir()
    if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
)
```
Filters for supported file types only; hidden files and other formats are ignored.

```python
if not doc_paths:
    raise FileNotFoundError(...)

missing_metadata = [path.name for path in doc_paths if path.name not in SOURCE_REGISTRY]
if missing_metadata:
    raise KeyError(...)
```
Two hard guards:
1. Raises `FileNotFoundError` if no supported documents exist — prevents a silent empty-pipeline run.
2. Raises `KeyError` if any filename has no registry entry — this enforces that every document that enters the pipeline has pre-vetted clinical metadata.

```python
registered_documents = [(path, SOURCE_REGISTRY[path.name]) for path in doc_paths]
```
The resulting list of `(Path, metadata_dict)` tuples is the primary iterable for parsing and chunking.

---

## Cell 6 — Install `google-genai`

### Cell Summary
A one-line `%pip install` magic command that installs the `google-genai` Python SDK, required for the Gemini Vision Language Model (VLM) calls in Cell 11.

### Code Explanation
```python
%pip install -q google-genai
```
The `-q` (quiet) flag suppresses verbose output. This cell is a dependency install step and must be run before any Gemini API calls. After running, a kernel restart may be required if the package is newly installed in the same session.

---

## Cell 7 — Docling Converter Configuration

### Cell Summary
Creates the `DocumentConverter` instance with high-fidelity PDF extraction settings: OCR enabled, table structure reconstruction enabled, page-level image generation, picture image extraction, and 2× image scale. This converter is reused for all documents in `registered_documents`.

### Code Explanation

```python
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.generate_page_images = True
pipeline_options.generate_picture_images = True
pipeline_options.images_scale = 2.0
```

- `do_ocr = True` — enables optical character recognition so text embedded as images in scanned PDFs is extracted.
- `do_table_structure = True` — instructs Docling's table recognition model to reconstruct rows and columns rather than treating tables as plain text blobs.
- `generate_page_images = True` — renders each PDF page as an image (needed for figure crops).
- `generate_picture_images = True` — extracts each `PictureItem` as a separate cropped PNG.
- `images_scale = 2.0` — doubles resolution (2× DPI) so small figures remain legible for the VLM.

```python
converter = DocumentConverter(
    format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}
)
```
The converter is scoped to PDFs only via `InputFormat.PDF`. The `PdfFormatOption` wrapper passes the custom `pipeline_options` into Docling's internal pipeline.

---

## Cell 8 — `file_sha256()` Helper

### Cell Summary
Defines a streaming SHA-256 file hasher that reads files in 64 KB chunks. Its output is used as the `content_hash` field in every chunk's metadata, enabling downstream systems to detect document tampering or unintentional re-ingestion of different file versions.

### Code Explanation
```python
def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
```
- Opens the file in binary mode (`"rb"`) to hash the raw bytes, not a decoded string.
- Uses `iter(callable, sentinel)` pattern — reads 65,536-byte blocks until `f.read()` returns an empty byte string.
- Returns a 64-character hex digest (256 bits). The first 12 characters are shown in log output for quick identification without full hash exposure.

---

## Cell 9 — Document Parsing with Cache & Artifact Export

### Cell Summary
The main PDF-to-structured-data extraction loop. For each registered document, it checks whether a cached `document.json` exists (Docling's native serialisation); if so it loads the cache; if not it runs the full Docling conversion, saves the JSON, exports each table as an HTML file, and saves each figure crop as a PNG. At the end it prints page counts, table counts, figure counts, and the first 12 characters of the content hash.

### Code Explanation

```python
parsed_docs = {}  # {doc_id: {"doc": DoclingDocument, "meta": dict, "out_dir": Path}}
```
Central store; all later cells read from this dict.

**Cache check:**
```python
json_path = out_dir / "document.json"
doc_hash = file_sha256(path)

if json_path.exists():
    doc = DoclingDocument.load_from_json(json_path)
else:
    result = converter.convert(path)
    if result.status != ConversionStatus.SUCCESS:
        raise RuntimeError(...)
    doc = result.document
    doc.save_as_json(json_path)
```
Caching avoids re-running expensive OCR/table detection (which can take several minutes per document). The cache key is the presence of `document.json`; the content hash is computed separately from the raw PDF file so it can detect if the source PDF was swapped out.

**Table HTML export:**
```python
for i, table in enumerate(doc.tables):
    (out_dir / f"table-{i:03d}.html").write_text(
        table.export_to_html(doc=doc), encoding="utf-8"
    )
```
Each table is exported as a lossless HTML artifact (preserving cell spans, row/column structure). These are referenced in `artifact_path` within child chunk metadata.

**Figure PNG export:**
```python
for i, picture in enumerate(doc.pictures):
    img = picture.get_image(doc)
    if img is not None:
        img.save(out_dir / f"picture-{i:03d}.png")
```
Each `PictureItem` crop is saved as a PNG. `get_image()` returns `None` for pictures Docling couldn't render (missing or corrupted), so the guard is essential.

**Result stored:**
```python
parsed_docs[doc_id] = {
    "doc": doc,
    "meta": {**meta, "content_hash": doc_hash, "filename": path.name},
    "out_dir": out_dir,
}
```
The `content_hash` is merged into the metadata dict so every downstream chunk carries it as a provenance field.

---

## Cell 10 — Structural Utility Functions

### Cell Summary
Defines five reusable helper functions that all later cells rely on for extracting page numbers, captions, list text, bounding boxes, and table footnotes from Docling document items. This cell also documents the `ListItem` ordering fix that prevents list items from being silently cast to plain prose.

### Code Explanation

**`get_page(item)`:**
```python
return item.prov[0].page_no if getattr(item, "prov", None) else None
```
`prov` (provenance) is a list of page-location records. Returns `None` for items without page anchoring (e.g., items in document preamble).

**`get_caption(item, doc)`:**
```python
return re.sub(r"\s+", " ", item.caption_text(doc) or "").strip()
```
Calls Docling's `.caption_text(doc)` method, then collapses whitespace. The `try/except` absorbs any API version differences where the method might not exist.

**`get_list_text(item, level)`:**
```python
marker = "  " * level + "• "
text = re.sub(r"\s+", " ", getattr(item, "text", "") or "").strip()
return f"{marker}{text}" if text else ""
```
Preserves list bullet markers with correct indentation. This is the **Fix 2a** in the pipeline: without this, list items would be treated as indistinguishable prose, losing their hierarchical clinical structure (e.g., warning sign bullet lists in dengue guidelines).

**`get_bbox(item)`:**
Returns the bounding box as a dict (via `.model_dump()`) or string, or `None` if no bounding box is available. Used for spatial provenance tracking.

**`_resolve_text(ann, doc)`:**
A private helper that resolves a Docling annotation reference to its text string. Handles both string annotations (direct text) and reference objects (using `.resolve(doc)` or falling back to `.text` attribute). Collapses whitespace regardless.

**`get_table_footnotes(item, doc)`:**
```python
for ann in getattr(item, "annotations", None) or []:
    _add(_resolve_text(ann, doc))
for fn in getattr(item, "footnotes", None) or []:
    _add(_resolve_text(fn, doc))
```
Checks both `item.annotations` (Docling 2.x standard) and `item.footnotes` (older Docling API) so the pipeline works across Docling versions. A `seen` set deduplicates footnotes that appear in both paths. Each footnote is prefixed with `[footnote]` so downstream text search can identify footnote content separately from main table content.

---

## Cell 11 — Document Structure Inventory & Logging

### Cell Summary
Iterates every document in `parsed_docs` and builds three in-memory logs: headings (with section hierarchy), tables (shape, section context, caption, footnotes), and figures (dimensions, section context, caption). Prints the first 15 entries of each log per document. This is an inspection/debugging cell, not a data-writing step.

### Code Explanation

```python
section_stack = []
for item, level in doc.iterate_items():
    page = get_page(item)
    if isinstance(item, (TitleItem, SectionHeaderItem)):
        txt = re.sub(r"\s+", " ", item.text or "").strip()
        if txt:
            while section_stack and section_stack[-1][0] >= level:
                section_stack.pop()
            section_stack.append((level, txt))
            headings_log.append((page, level, " > ".join(h for _, h in section_stack)))
```
The `section_stack` is a lightweight breadcrumb trail. When a heading at level N is encountered, all stack entries at level ≥ N are popped (they are sub-headings of a sibling or ancestor), then the current heading is pushed. The resulting `" > ".join(...)` gives a fully-qualified section path like `"Clinical Management > Fluid Management > Oral Rehydration"`.

```python
elif isinstance(item, ListItem):   # Fix 5: BEFORE TextItem
    if get_list_text(item, level).strip():
        counts["lists"] += 1
elif isinstance(item, TextItem):
    if (item.text or "").strip():
        counts["text"] += 1
```
`ListItem` is checked before `TextItem` because `ListItem` subclasses `TextItem` in Docling 2.x; without this order, list items would be counted and processed as generic text.

**Table log entry:**
```python
rows = getattr(getattr(item, "data", None), "num_rows", "?")
cols = getattr(getattr(item, "data", None), "num_cols", "?")
fn   = get_table_footnotes(item, doc).replace("\n", " ")
```
Uses chained `getattr` with fallback `"?"` to safely access row/column counts in case the `data` attribute structure changes across Docling versions.

**Figure log entry:**
```python
img  = item.get_image(doc)
dims = f"{img.size[0]}x{img.size[1]}" if img else "missing"
```
Reports pixel dimensions so reviewers can spot figures that are too small to be clinically meaningful.

---

## Cell 12 — `inspect_page()` Helper

### Cell Summary
Defines and immediately calls `inspect_page()`, a debugging tool that prints every extracted item on a specified page of a specified document. It serves as a spot-check mechanism to verify that Docling's extraction is accurate before committing chunks to SQLite.

### Code Explanation

```python
def inspect_page(doc_id: str, target_page: int):
    doc = parsed_docs[doc_id]["doc"]
    for item, level in doc.iterate_items():
        if get_page(item) != target_page:
            continue
        kind = type(item).__name__
        if isinstance(item, TableItem):
            fn = get_table_footnotes(item, doc)
            preview = item.export_to_markdown(doc=doc)[:200].replace("\n", " | ")
            if fn:
                preview += f" || {fn[:100]}"
        elif isinstance(item, PictureItem):
            dims = f"{img.size[0]}x{img.size[1]}" if img else "missing"
            preview = f"[IMAGE {dims}] caption={get_caption(item, doc)!r}"
        elif isinstance(item, ListItem):
            preview = get_list_text(item, level)[:160]
        else:
            preview = re.sub(r"\s+", " ", getattr(item, "text", "") or "").strip()[:160]
        print(f"[{kind:<17} L{level}] {preview}")
```

Each item is dispatched by type and formatted with:
- **Tables** — Markdown preview (first 200 chars) with footnotes appended after `||`.
- **Pictures** — Pixel dimensions + caption.
- **Lists** — Indented bullet with level.
- **All others** — First 160 chars of plain text.

The cell calls `inspect_page("who_arboviral_guideline_2025", 10)` as the demo invocation to show page 10 of the WHO arboviral guidelines. Adjust the arguments to inspect any page of any loaded document.

---

## Cell 13 — Figure Inventory & Size Filtering

### Cell Summary
Builds the `figure_inventory` list by iterating every document's `PictureItem` elements, checking whether the saved PNG exists on disk, measuring its pixel dimensions, and assigning a `review_status` of `pending_vlm` (ready for Gemini), `skipped_small` (below 120px threshold), or `missing_image`. Prints summary counts at the end.

### Code Explanation

**Min-size threshold:**
```python
MIN_FIGURE_PX = 120  # Skip small icons, logos, or decorative lines
```
Figures with either width or height below 120 pixels are likely icons, decorative separators, or watermarks — not clinical diagrams worth sending to the VLM.

**Index resolution:**
```python
ref = getattr(item, "self_ref", "")
if ref.startswith("#/pictures/"):
    pic_idx = int(ref.split("/")[-1])
else:
    pic_idx = fallback_idx
fallback_idx += 1
```
Docling stores a `self_ref` like `"#/pictures/5"` on each `PictureItem`. This is used to find the matching saved PNG (`picture-005.png`). The `fallback_idx` counter handles any items without a `self_ref`.

**Status assignment:**
```python
if not img_path.exists():
    status = "missing_image"; is_relevant = False
elif w < MIN_FIGURE_PX or h < MIN_FIGURE_PX:
    status = "skipped_small"; is_relevant = False
else:
    status = "pending_vlm"; is_relevant = True
```

**Inventory record:**
```python
figure_inventory.append({
    "figure_id": f"{doc_id}__fig_{pic_idx:03d}",
    "doc_id": doc_id,
    "source_pdf": bundle["meta"]["filename"],
    "source": bundle["meta"]["source"],
    "page": get_page(item),
    "bbox": get_bbox(item),
    "section_path": " > ".join(h for _, h in section_stack) or "Document Root",
    "caption": get_caption(item, doc),
    "image_path": str(img_path),
    "width": w,
    "height": h,
    "is_relevant": is_relevant,
    "review_status": status,
})
```
The `section_path` at the time of the figure is computed from the same `section_stack` updated by headings encountered before this figure in reading order.

---

## Cell 14 — Gemini VLM Figure Captioning

### Cell Summary
Sends each `pending_vlm` figure (up to `TEST_LIMIT=3` by default) to Gemini 2.5 Flash using a strict JSON prompt that requests figure type classification, a faithful description, structured node/edge logic (for flowcharts), and a list of ambiguous/unreadable elements. Results are checkpointed to `figures_manifest.json` after each figure. Already-processed figures are skipped (cached), and errors are caught and stored as `vlm_error` without halting the pipeline.

### Code Explanation

**Prompt design:**
```
FIGURE_PROMPT = """
You are digitizing a figure from a dengue clinical guideline for offline review.
Do NOT invent clinical advice or extrapolate beyond what is literally visible.
Set "is_relevant" to false for logos, cover art, or purely decorative graphics.
Return STRICT JSON: { "is_relevant": ..., "figure_type": ..., "description": ...,
  "structured_logic": {"nodes": [...], "edges": [...]}, "ambiguous_elements": [...] }
"""
```
The safety instruction "Do NOT invent clinical advice" is critical: the VLM must transcribe what is literally visible, not interpret or extrapolate. Setting `temperature=0.0` enforces determinism.

**Context hint:**
```python
context_hint = (
    f"Document: {fig['doc_id']} | Page: {fig['page']} | "
    f"Section: {fig['section_path']} | Caption: {fig['caption'] or 'None'}"
)
```
Gives the VLM page-level context so it can better interpret unlabelled axes or partial diagrams.

**Lazy client initialization:**
```python
if client_genai is None:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set in environment variables.")
    client_genai = genai.Client(api_key=api_key)
```
The API client is only created on the first figure that actually needs VLM processing. If all figures are cached, the cell completes without touching the API key — this avoids failures in offline environments.

**API call:**
```python
response = client_genai.models.generate_content(
    model=VLM_MODEL,
    contents=[FIGURE_PROMPT, context_hint, pil_img],
    config=types.GenerateContentConfig(
        response_mime_type="application/json",
        temperature=0.0,
    ),
)
```
`response_mime_type="application/json"` forces Gemini to return valid JSON (rather than prose with embedded JSON), which the pipeline then parses directly.

**Post-processing:**
```python
is_rel = bool(vlm_out.get("is_relevant", True))
saved_records[fid] = {
    ...
    "review_status": "pending_review" if is_rel else "skipped_decorative",
}
```
Relevant figures advance to `pending_review` (requiring human HITL sign-off before entering the vector index). Decorative figures get `skipped_decorative` and are never indexed.

**Error handling:**
```python
except Exception as e:
    saved_records[fid] = {**fig, "vlm_model": VLM_MODEL, "review_status": "vlm_error", "error": str(e), ...}
    FIGURES_MANIFEST_PATH.write_text(...)
    continue
```
Error records are checkpointed immediately and the loop continues with the next figure. `vlm_error` figures will be retried on the next run (the cache-skip condition excludes `pending_vlm` and `vlm_error` statuses).

---

## Cell 15 — Reset Stale Chunk Stores

### Cell Summary
A maintenance cell controlled by the `RESET_STALE_STORE` boolean flag. When set to `True`, it deletes the SQLite database (`guarddengue_chunks.db`) and the Qdrant local store directory (`qdrant_local/`), including WAL/SHM/journal files. Crucially, it **preserves** all Docling-cached artifacts (`document.json`, HTML tables, PNG figures, `figures_manifest.json`). This should be run once after switching to UUID5 chunk IDs, then reset to `False`.

### Code Explanation

```python
RESET_STALE_STORE = True

_db   = EXTRACTED_DIR / "guarddengue_chunks.db"
_qdir = EXTRACTED_DIR / "qdrant_local"
```
The flag guards the destructive operation. Setting it to `True` triggers the cleanup.

```python
for db_file in (_db, Path(f"{_db}-wal"), Path(f"{_db}-shm"), Path(f"{_db}-journal")):
    if db_file.exists():
        db_file.unlink()
        deleted.append(str(db_file))
if _qdir.exists():
    shutil.rmtree(_qdir)
    deleted.append(str(_qdir))
```
SQLite WAL (Write-Ahead Logging) and SHM (shared memory) files must be deleted alongside the main `.db` file or they can corrupt a fresh database. `shutil.rmtree` removes the entire Qdrant local storage directory tree.

**PermissionError guard:**
```python
except PermissionError as e:
    raise RuntimeError(
        f"Store file is still locked ({e}). Close open SQLite/Qdrant connections or restart the kernel..."
    ) from e
```
On Windows, SQLite files remain locked if another process (or the same kernel session) has an open connection. The error message tells the user exactly what to do.

---

## Cell 16 — Parent-Child Chunker and SQLite Schema

### Cell Summary
The core chunking cell. Defines the SQLite schema (`parent_chunks`, `child_chunks` tables), helper functions for content hashing and deterministic chunk ID generation, and the main `build_parent_child_chunks()` function that groups document items by section, produces atomic child chunks (prose batches ≤ 1200 chars; tables and figures always atomic), writes parent and child rows to SQLite with upsert-on-conflict semantics, and builds `llama_index` `TextNode` objects with PARENT / PREV / NEXT relationships.

### Code Explanation

**SQLite schema:**
```sql
CREATE TABLE IF NOT EXISTS parent_chunks (
    parent_id      TEXT PRIMARY KEY,
    doc_id         TEXT NOT NULL,
    section_path   TEXT NOT NULL,
    page_start     INTEGER, page_end INTEGER,
    text           TEXT NOT NULL,
    metadata_json  TEXT NOT NULL,
    review_status  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS child_chunks (
    chunk_id           TEXT PRIMARY KEY,
    parent_id          TEXT NOT NULL REFERENCES parent_chunks(parent_id),
    doc_id             TEXT NOT NULL,
    element_type       TEXT NOT NULL,
    section_path       TEXT NOT NULL,
    page_start         INTEGER, page_end INTEGER,
    bbox_json          TEXT,
    artifact_ref       TEXT,  -- e.g. "who_arboviral__table_003"
    artifact_path      TEXT,  -- file path to HTML or PNG
    text               TEXT NOT NULL,
    metadata_json      TEXT NOT NULL,
    review_status      TEXT NOT NULL,
    chunk_content_hash TEXT,  -- SHA-256 of normalised chunk text (Fix 3)
    reviewed_at        TEXT,  -- UTC ISO timestamp set on approval; NULL until then
    superseded_by      TEXT   -- chunk_id of replacement; NULL = current (Fix 3)
);
```
`REFERENCES parent_chunks(parent_id)` enforces referential integrity when `PRAGMA foreign_keys = ON` is active. The `superseded_by` column enables a soft-delete / audit-trail pattern: old chunk versions are never deleted, only marked superseded.

**Safe column-add (idempotent schema migration):**
```python
for col, ddl in [("chunk_content_hash", "TEXT"), ("reviewed_at", "TEXT"), ("superseded_by", "TEXT")]:
    try:
        conn.execute(f"ALTER TABLE child_chunks ADD COLUMN {col} {ddl}")
        conn.commit()
    except Exception:
        pass  # column already exists
```
Allows the schema to evolve without breaking existing databases — the `ALTER TABLE` silently fails if the column already exists.

**`chunk_content_sha256(text)`:**
```python
normalised = re.sub(r"\s+", " ", text).strip()
return hashlib.sha256(normalised.encode("utf-8")).hexdigest()
```
Normalises whitespace before hashing so reformatted text with identical content gets the same hash. This is used as part of the chunk ID seed and for drift detection.

**`make_chunk_id(doc_id, section_path, element_type, content_hash, occurrence_idx)`:**
```python
seed = f"{doc_id}|{section_path}|{element_type}|{content_hash}|{occurrence_idx}"
return str(uuid.uuid5(uuid.NAMESPACE_URL, seed))
```
UUID5 is deterministic: the same inputs always produce the same ID. The `occurrence_idx` counter handles collision when the same text genuinely appears multiple times in the same section (e.g., repeated disclaimer paragraphs).

**`build_parent_child_chunks()` — Section grouping phase:**
```python
sections = []
current  = {"section_path": "Document Root", "items": [], "pages": []}
section_stack = []

for item, level in doc.iterate_items():
    if isinstance(item, (TitleItem, SectionHeaderItem)):
        if heading:
            if current["items"]:
                sections.append(current)
            # rebuild section_path from stack
            current = {"section_path": ..., "items": [], "pages": [...]}
    elif isinstance(item, ListItem):   # Fix 5: BEFORE TextItem
        current["items"].append({"type": "prose", "text": get_list_text(...), ...})
    elif isinstance(item, TextItem):
        current["items"].append({"type": "prose", "text": txt, ...})
    elif isinstance(item, TableItem):
        # Builds block: "[TABLE {id}] {caption}\n{markdown}\n{footnotes}"
        current["items"].append({"type": "table", ...})
    elif isinstance(item, PictureItem):
        # Looks up VLM description from figures_by_id
        fig_text = "[FIGURE {id}] {caption}\nType: ...\nDescription: ...\nNodes: ...\nEdges: ...\nAmbiguous: ..."
        # Figures from quarantined docs remain "quarantined"; others become "pending_review"
        current["items"].append({"type": "figure", "item_status": "quarantined" if doc_status == "quarantined" else "pending_review", ...})
```

**Child chunk assembly — `flush_prose()` pattern:**
```python
MAX_PROSE_CHARS = 1200
prose_buf = []
for entry in sec["items"]:
    if entry["type"] == "prose":
        if prose_buf and (sum(len(t) for t in prose_buf) + len(entry["text"]) > MAX_PROSE_CHARS):
            flush_prose()
        prose_buf.append(entry["text"])
    else:
        flush_prose()   # flush accumulated prose before a table or figure
        children.append({...})  # tables/figures are always atomic
flush_prose()  # flush any trailing prose
```
Prose items are batched into child chunks up to 1200 characters. Tables and figures interrupt any pending prose batch and are always emitted as individual, indivisible chunks (never split mid-row or mid-figure).

**SQLite upsert (ON CONFLICT DO UPDATE):**
```python
conn.execute("""
    INSERT INTO child_chunks ... VALUES (?, ?, ...)
    ON CONFLICT(chunk_id) DO UPDATE SET
        ...,
        reviewed_at   = COALESCE(child_chunks.reviewed_at, excluded.reviewed_at),
        superseded_by = COALESCE(child_chunks.superseded_by, excluded.superseded_by)
""", (...))
```
The `COALESCE` guards on `reviewed_at` and `superseded_by` ensure that if a chunk was already approved or superseded, re-running the chunker does not accidentally clear those fields.

**LlamaIndex `TextNode` relationship graph:**
```python
node = TextNode(id_=chunk_id, text=ch["text"], metadata=child_meta)
node.relationships[NodeRelationship.PARENT] = RelatedNodeInfo(node_id=parent_id)
if prev_chunk_id:
    node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(node_id=prev_chunk_id)
    llama_nodes[-1].relationships[NodeRelationship.NEXT] = RelatedNodeInfo(node_id=chunk_id)
```
Each chunk knows its parent (the section), its previous sibling, and its next sibling. This doubly-linked structure enables context window expansion during retrieval without re-querying SQLite.

---

## Cell 17 — `check_release_sync()` v1 (Corpus Tag Verification)

### Cell Summary
Defines and immediately calls the first version of `check_release_sync()`. It verifies that SQLite (approved active chunks), Qdrant (all indexed points), and the local `safety_policy_{CORPUS_RELEASE}.json` file all carry the same `CORPUS_RELEASE` tag. Neo4j is checked if `NEO4J_PASSWORD` is set; otherwise that check is skipped gracefully.

### Code Explanation

**SQLite check:**
```sql
SELECT COUNT(*), COALESCE(SUM(
    CASE WHEN json_extract(metadata_json, '$.corpus_release') IS NOT ? THEN 1 ELSE 0 END
), 0)
FROM child_chunks
WHERE review_status = 'approved' AND superseded_by IS NULL
```
Uses `json_extract` to read the embedded `corpus_release` field. The `IS NOT` operator handles `NULL` comparisons correctly (unlike `!=`). Reports how many active approved chunks have a mismatched or missing release tag.

**Qdrant paginated scan:**
```python
while True:
    points, offset = qdrant.scroll(collection_name=COLLECTION_NAME, limit=256, offset=offset, with_payload=True, with_vectors=False)
    total_q += len(points)
    bad_q += sum(1 for p in points if (p.payload or {}).get("corpus_release") != tag)
    if not points or offset is None:
        break
```
Full paginated scan (256 points per page) counts how many Qdrant payloads have the wrong or missing `corpus_release`.

**Policy JSON check:**
```python
policy_data = json.loads(policy_path.read_text(encoding="utf-8"))
rules = policy_data.get("rules", [policy_data]) if isinstance(policy_data, dict) else policy_data
bad_p = [r for r in rules if not isinstance(r, dict) or r.get("corpus_release") != tag]
```
Handles both a top-level list of rules and a `{"rules": [...]}` envelope format.

**Neo4j check (optional):**
```cypher
MATCH ()-[r:AVOID_IN]->()
WHERE r.corpus_release IS NULL OR r.corpus_release <> $tag
RETURN count(r) AS n
```
Counts graph edges in Neo4j whose `corpus_release` is stale. Skipped if `NEO4J_PASSWORD` is not set.

---

## Cell 18 — Chunk Count Summary & Parent-Child Sample Inspector

### Cell Summary
Queries SQLite to print a table of active chunk counts grouped by `doc_id`, `element_type`, and `review_status`. Then finds a sample parent section that contains at least one table or figure child and prints all its children with previews. This is a human-readable audit of what the chunker produced.

### Code Explanation

**Count query:**
```sql
SELECT doc_id, element_type, review_status, COUNT(*)
FROM child_chunks
WHERE superseded_by IS NULL
GROUP BY doc_id, element_type, review_status
ORDER BY doc_id, element_type, review_status
```
The `superseded_by IS NULL` filter ensures only active (non-superseded) chunks are counted.

**Sample parent query:**
```sql
SELECT DISTINCT p.parent_id, p.doc_id, p.section_path, p.page_start, p.page_end
FROM parent_chunks p
JOIN child_chunks c ON p.parent_id = c.parent_id
WHERE c.element_type IN ('figure', 'table')
  AND c.superseded_by IS NULL
LIMIT 1
```
Specifically selects a section containing a figure or table so the inspector demonstrates the most complex chunk type.

**Child display:**
```python
for cid, el_type, pg, art, status, preview in children:
    print(f"  -> {cid} | type={el_type} | p.{pg} | status={status}")
    if art:
        print(f"     artifact: {art}")
    print(f"     preview : {preview.replace(chr(10), ' ')}...")
```
Shows `artifact_path` (the HTML or PNG file path) for structured elements, which is crucial for HITL reviewers who need to open the original file.

---

## Cell 19 — Install `qdrant-client` and `fastembed`

### Cell Summary
A one-line `%pip install` that installs the Qdrant vector database client and the FastEmbed embedding library (used for both dense and sparse embeddings without a separate embedding server).

### Code Explanation
```python
%pip install qdrant-client fastembed
```
`qdrant-client` provides the Python API for the local Qdrant instance (stored in `extracted/qdrant_local/`). `fastembed` provides:
- **Dense embeddings** via a compact transformer model (e.g., `BAAI/bge-small-en-v1.5`)
- **Sparse embeddings** via BM25/SPLADE-style models for keyword-sensitive retrieval

These are used in the Qdrant upsert cell and all retrieval cells. The embedder variables (`dense_embedder`, `sparse_embedder`, `qdrant`) are expected to be initialised in the kernel session before the next cell runs (typically by an implicit or companion setup cell that initialises these after the pip install).

---

## Cell 20 — HITL Governance Tables and Review Functions

### Cell Summary
Provisions three additional SQLite tables (`review_tasks`, `derived_artifacts`, `review_events`) and defines the full Human-in-the-Loop (HITL) review API: `approve_document_text_and_tables()`, `record_figure_decision()`, `list_pending_figures()`, and `inspect_figure()`. These functions enforce that no chunk enters the vector index without documented clinical sign-off.

### Code Explanation

**`review_tasks` table:**
```sql
CREATE TABLE IF NOT EXISTS review_tasks (
    task_id        TEXT PRIMARY KEY,
    object_id      TEXT NOT NULL,
    object_type    TEXT NOT NULL,  -- 'document_text_tables' | 'figure'
    object_hash    TEXT NOT NULL,
    corpus_release TEXT NOT NULL,
    assigned_role  TEXT NOT NULL DEFAULT 'clinical_reviewer',
    status         TEXT NOT NULL,
    created_at     TEXT NOT NULL, updated_at TEXT NOT NULL,
    UNIQUE(object_id, object_hash, corpus_release)
)
```
One task per (object, hash, release) triple — if the content changes (new hash), a new task is created.

**`derived_artifacts` table:**
Stores corrected text versions of figures. When a reviewer submits `decision="correct"`, the correction is written here (with `source_chunk_id`, `prior_hash`, `corrected_text`, `resulting_hash`) but the original VLM PNG on disk is **never overwritten**.

**`review_events` table:**
An append-only audit log. Every decision (`approve`, `reject`, `correct`, `release_from_quarantine`) is recorded with `reviewer_id`, `rationale`, and before/after hashes. The `_append_review_event()` helper validates that `reviewer_id` is not a placeholder string and that `rationale` is non-empty before writing.

**`approve_document_text_and_tables(doc_id, reviewer_id, rationale)`:**
```python
rows = conn.execute("""
    SELECT chunk_id, element_type, review_status, chunk_content_hash, metadata_json
    FROM child_chunks
    WHERE doc_id = ? AND superseded_by IS NULL
      AND json_extract(metadata_json, '$.corpus_release') = ?
""", (doc_id, CORPUS_RELEASE)).fetchall()

if not first_meta.get("publication_date"):
    raise ValueError(f"Cannot approve {doc_id!r}: verified publication_date is missing...")
```
Key safety rules:
1. Requires a confirmed `publication_date` — quarantined documents are blocked.
2. Approves `prose` and `table` chunks directly (setting `review_status = 'approved'`, `reviewed_at = now`).
3. Figure chunks from quarantined docs: released to `'pending_review'` (NEVER auto-approved).
4. Figure chunks already in `pending_review`: a task record is ensured but no status change.
5. Parent chunks are marked `'approved'` so retrieval can confirm section-level approval.

**`record_figure_decision(chunk_id, reviewer_id, decision, rationale, corrected_text, rejection_reason)`:**
Implements a state machine for figures:
- `pending_review` or `corrected_pending_review` → `approve`: sets `review_status='approved'`, `reviewed_at=now`.
- → `reject`: requires `rejection_reason`; sets `review_status='rejected'`, `reviewed_at=NULL`.
- → `correct`: requires `corrected_text`; computes `new_hash`, inserts `derived_artifacts` record, updates chunk text and hash, sets `review_status='corrected_pending_review'`. The old task is closed and a new task is opened bound to the new hash. The corrected chunk **must be re-reviewed** (approved) before release.

**`list_pending_figures(limit=20)`:**
```sql
SELECT chunk_id, doc_id, page_start, review_status, section_path,
       json_extract(metadata_json, '$.artifact_path'), substr(text, 1, 140)
FROM child_chunks
WHERE element_type = 'figure'
  AND review_status IN ('pending_review', 'corrected_pending_review')
  AND superseded_by IS NULL
  AND json_extract(metadata_json, '$.corpus_release') = ?
ORDER BY doc_id, page_start, rowid
LIMIT ?
```
Returns the active figure review queue for the current release, sorted by document and page order.

**`inspect_figure(chunk_id)`:**
Displays chunk metadata, the current text (VLM description or corrected text), renders the PNG via `IPython.display.Image` if available on disk, and prints the full audit history from `review_events`.

---

## Cell 21 — Qdrant Collection Setup, Batch Embedding, and Release Promotion

### Cell Summary
The largest operational cell. It: (1) provisions the `release_manifests` SQLite table; (2) names the Qdrant collection `guarddengue_{CORPUS_RELEASE}`; (3) fetches all active approved chunks from SQLite; (4) computes a canonical manifest hash; (5) creates the Qdrant collection with dense (cosine) + sparse (IDF-weighted) vector configs; (6) batch-embeds and upserts all approved chunks; (7) prunes stale Qdrant points; (8) verifies exact ID/count parity; (9) writes/promotes the `release_manifests` entry to `'active'`.

### Code Explanation

**`release_manifests` table:**
```sql
CREATE TABLE IF NOT EXISTS release_manifests (
    release_id      TEXT PRIMARY KEY,
    collection_name TEXT NOT NULL,
    manifest_sha256 TEXT NOT NULL,
    sqlite_count    INTEGER NOT NULL,
    qdrant_count    INTEGER NOT NULL,
    policy_count    INTEGER NOT NULL,
    promoted_by     TEXT,
    promoted_at     TEXT,
    status          TEXT NOT NULL   -- 'staged' | 'active' | 'superseded' | 'failed'
);
```
Provides an auditable record of every release promotion attempt.

**Collection naming:**
```python
COLLECTION_NAME = f"guarddengue_{CORPUS_RELEASE}"
```
Release-scoped names (`guarddengue_v0.1-dev`, `guarddengue_v1.0`) ensure new releases index into a fresh collection and cannot overwrite or contaminate the previous release's points.

**Manifest hash computation:**
```python
def _compute_manifest_hash(pairs: list[tuple[str, str]], release_id: str) -> str:
    canonical = json.dumps(
        {"release_id": release_id, "chunks": sorted(pairs)},
        sort_keys=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```
A deterministic fingerprint of the full set of `(chunk_id, chunk_content_hash)` pairs for the release. Any change to any chunk's content, or addition/removal of a chunk, changes this hash.

**Qdrant collection creation:**
```python
qdrant.create_collection(
    collection_name=collection_name,
    vectors_config={"dense": models.VectorParams(size=vector_size, distance=models.Distance.COSINE)},
    sparse_vectors_config={"sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)},
)
```
Hybrid (dense + sparse) collection. The IDF modifier weights sparse vector terms by inverse document frequency, boosting rare clinical terminology.

**Batch embed & upsert:**
```python
for start in range(0, len(active_rows), BATCH_SIZE):
    batch = active_rows[start : start + BATCH_SIZE]
    texts = [r[10] for r in batch]
    dense_vecs = [v.tolist() for v in dense_embedder.embed(texts)]
    sparse_vecs = list(sparse_embedder.embed(texts))
    points = [
        models.PointStruct(
            id=cid,
            vector={"dense": d_vec, "sparse": models.SparseVector(indices=s_vec.indices.tolist(), values=s_vec.values.tolist())},
            payload={...full provenance fields...},
        )
        for row, d_vec, s_vec in zip(batch, dense_vecs, sparse_vecs)
    ]
    qdrant.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
```
Batches of 32 chunks are embedded at once. `wait=True` ensures upserts are durably committed before proceeding.

**Stale point pruning:**
```python
stale_ids = sorted(existing_ids - expected_ids)
if stale_ids:
    for i in range(0, len(stale_ids), 256):
        qdrant.delete(collection_name=COLLECTION_NAME,
                      points_selector=models.PointIdsList(points=stale_ids[i:i+256]), wait=True)
```
Removes any Qdrant point whose chunk_id is no longer in the active approved SQLite set (e.g., superseded or unapproved chunks from a previous run).

**Parity check and manifest promotion:**
```python
if final_qdrant_count != len(expected_ids):
    conn.execute("INSERT OR REPLACE INTO release_manifests ... VALUES (..., 'failed')", ...)
    raise RuntimeError(f"Release {CORPUS_RELEASE} parity failed...")

conn.execute("UPDATE release_manifests SET status = 'superseded' WHERE status = 'active'")
conn.execute("INSERT OR REPLACE INTO release_manifests ... VALUES (..., 'active')", ...)
```
Previous `'active'` releases are marked `'superseded'` before the new one is written. If parity fails, a `'failed'` record is written and an exception is raised — the pipeline never silently promotes a broken release.

---

## Cell 22 — `check_release_sync()` v2 (Full Cross-Store Verification)

### Cell Summary
Defines the production-grade version of `check_release_sync()` that verifies exact ID-set **and** content-hash parity across SQLite, Qdrant, `release_manifests`, and the local policy JSON. Also validates Neo4j if configured. Returns `True` only if all checks pass.

### Code Explanation

**SQLite → dict:**
```python
sqlite_rows = conn.execute("""
    SELECT chunk_id, chunk_content_hash
    FROM child_chunks
    WHERE review_status = 'approved' AND superseded_by IS NULL
      AND json_extract(metadata_json, '$.corpus_release') = ?
""", (CORPUS_RELEASE,)).fetchall()
sqlite_map = {cid: chash for cid, chash in sqlite_rows}
sqlite_ids = set(sqlite_map.keys())
```

**Qdrant paginated scan with inline validation:**
```python
for pt in pts:
    pl = pt.payload or {}
    if (pl.get("corpus_release") != CORPUS_RELEASE
        or pl.get("review_status") != "approved"
        or pl.get("superseded_by") is not None):
        return False  # immediate fail
    qdrant_map[str(pt.id)] = pl.get("chunk_content_hash")
```
Every point is validated on the fly; a single bad payload causes immediate failure rather than counting and reporting.

**ID-set and hash-set equality:**
```python
if sqlite_ids != qdrant_ids:
    return False
hash_mismatches = [cid for cid in sqlite_ids if sqlite_map[cid] != qdrant_map.get(cid)]
if hash_mismatches:
    return False
```
Two-phase check: first the ID sets must be identical, then each chunk's hash must match between stores.

**Manifest validation:**
```python
expected_manifest = _compute_manifest_hash(sorted(sqlite_map.items()), CORPUS_RELEASE)
if manifest_row[0] != expected_manifest:
    return False  # manifest drift detected
```
Recomputes the manifest hash from live SQLite data and compares it with the stored manifest — detects out-of-band modifications to either store.

**Policy file validation:**
```python
for r in rules:
    if r.get("corpus_release") != CORPUS_RELEASE:
        return False
    cid = prov.get("chunk_id")
    if cid not in sqlite_map:
        return False  # rule references non-active chunk
    if prov.get("chunk_content_hash") and prov.get("chunk_content_hash") != sqlite_map[cid]:
        return False  # hash drift in policy provenance
```
Every policy rule's provenance `chunk_id` must still exist in the active approved SQLite set, and its hash must not have drifted.

---

## Cell 23 — Clinical Assertion Pinning and Safety Policy Compilation

### Cell Summary
Defines `find_approved_chunks()` for exploring the SQLite corpus, then implements fail-closed clinical assertion pinning: the reviewer manually sets `PINNED_NSAID_CHUNK_ID` and `CLINICAL_REVIEWER_ID` after inspecting the evidence, defines the full `REVIEWED_ASSERTIONS_SPEC` schema (NSAID contraindication in suspected dengue), validates every field, cross-checks the pinned chunk against SQLite, and writes the versioned `safety_policy_{CORPUS_RELEASE}.json` artifact. Calls `check_release_sync()` at the end.

### Code Explanation

**`find_approved_chunks(keyword, doc_id, limit)`:**
```python
sql = """
    SELECT chunk_id, doc_id, page_start, section_path, substr(text, 1, 200)
    FROM child_chunks
    WHERE review_status = 'approved' AND superseded_by IS NULL
      AND json_extract(metadata_json, '$.corpus_release') = ?
      AND lower(text) LIKE ?
"""
```
Full-text search over approved chunks using `LIKE`. Optional `doc_id` filter narrows to a specific document. This is used by reviewers to locate the exact guideline passage before pinning it.

**Manual chunk pinning:**
```python
PINNED_NSAID_CHUNK_ID = None   # e.g. "a1b2c3d4-..."
CLINICAL_REVIEWER_ID = None    # e.g. "dr_name_or_reviewer_id"
```
Both must be set by a human before the compilation block runs. The pipeline never auto-selects the first search result.

**`REVIEWED_ASSERTIONS_SPEC`:**
```python
REVIEWED_ASSERTIONS_SPEC = [{
    "assertion_id": "avoid_nsaids_suspected_dengue_v1",
    "assertion_type": "MEDICATION_CONTRAINDICATION",
    "relation": "AVOID_IN",
    "drug_class": {"id": "nsaids", "name": "NSAIDs"},
    "drug_members": [
        {"id": "aspirin", "name": "Aspirin", "aliases": ["acetylsalicylic acid", "asa", "ecosprin", "disprin"]},
        {"id": "ibuprofen", "name": "Ibuprofen", "aliases": ["brufen", "ibugesic", "advil", "motrin"]},
        # ... diclofenac, naproxen, mefenamic acid, aceclofenac, nimesulide
    ],
    "clinical_context": {"id": "suspected_dengue", "name": "Suspected dengue"},
    "jurisdiction": "WHO_GLOBAL",
    "population": "all_ages_suspected_dengue",
    "exclusions": ["Do not advise stopping an existing prescribed antiplatelet or chronic medication without clinician review."],
    "conflict_status": "none",
    "rationale": "Avoid NSAIDs such as aspirin and ibuprofen in suspected dengue because of bleeding risk...",
    "source_chunk_id": PINNED_NSAID_CHUNK_ID,
    "review_status": "approved",
    "reviewed_by": CLINICAL_REVIEWER_ID,
    "reviewed_at": datetime.now(timezone.utc).isoformat(),
}]
```

**Fail-closed validation loop:**
```python
for spec in REVIEWED_ASSERTIONS_SPEC:
    missing = [f for f in REQUIRED_ASSERTION_FIELDS if not spec.get(f)]
    if missing:
        raise ValueError(f"Fail-closed: assertion ... missing required fields {missing}. Pin PINNED_NSAID_CHUNK_ID...")
    if spec["reviewed_by"] in ("pending_clinical_signoff", "TBD", "prototype"):
        raise ValueError(...)
    if spec["review_status"] != "approved":
        raise ValueError(...)
```
Any missing field, placeholder reviewer, or non-approved status raises immediately — the policy file is never written with incomplete data.

**SQLite chunk cross-verification:**
```python
row = conn.execute("SELECT chunk_id, ... FROM child_chunks WHERE chunk_id = ?", (spec["source_chunk_id"],)).fetchone()
if not row:
    raise KeyError(f"source_chunk_id not found in SQLite: ...")
if row[6] != "approved":
    raise ValueError(f"Blocked unapproved evidence chunk: ...")
if row[7] is not None:
    raise ValueError(f"Blocked superseded evidence chunk: ...")
if meta.get("corpus_release") != CORPUS_RELEASE:
    raise ValueError(f"Blocked release-mismatched chunk: ...")
if not meta.get("publication_date"):
    raise ValueError(f"Blocked chunk missing publication_date: ...")
```
Five-layer SQLite gate: existence, approval status, supersession status, release match, and publication date presence.

**Policy artifact output:**
```python
compiled_assertions.append({**spec, "corpus_release": CORPUS_RELEASE, "provenance": {
    "doc_id": row[2], "source": meta["source"], "document_version": meta["document_version"],
    "publication_date": meta["publication_date"], "content_hash": meta["content_hash"],
    "chunk_content_hash": row[8], "parent_id": row[1], "section_path": row[3],
    "chunk_id": row[0], "page_start": row[4], "page_end": row[5],
}})
POLICY_ARTIFACT_PATH.write_text(json.dumps(compiled_assertions, indent=2), encoding="utf-8")
```
Full provenance (`doc_id`, `source`, `section_path`, `page_start`, `page_end`, `chunk_id`, `chunk_content_hash`) is embedded in every compiled rule, making each policy rule independently verifiable.

---

## Cell 24 — Neo4j Knowledge Graph Loading

### Cell Summary
Optionally loads compiled clinical assertions into a Neo4j knowledge graph. Defines schema constraints, an idempotent upsert Cypher template, and two stale-edge pruning queries. Skipped if `NEO4J_PASSWORD` is not set. Runs `check_release_sync()` after a successful load.

### Code Explanation

**Environment config:**
```python
NEO4J_URI      = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")
NEO4J_DATABASE = os.environ.get("NEO4J_DATABASE", "neo4j")
```

**Schema constraints:**
```python
SCHEMA_CONSTRAINTS = [
    "CREATE CONSTRAINT doc_id_unique IF NOT EXISTS FOR (d:Document) REQUIRE d.doc_id IS UNIQUE",
    "CREATE CONSTRAINT chunk_id_unique IF NOT EXISTS FOR (c:EvidenceChunk) REQUIRE c.chunk_id IS UNIQUE",
    "CREATE CONSTRAINT drug_id_unique IF NOT EXISTS FOR (dr:Drug) REQUIRE dr.id IS UNIQUE",
    # ... Section, DrugClass, ClinicalContext
]
```

**`UPSERT_ASSERTION_CYPHER`:**
The Cypher template uses `MERGE` (upsert) for all nodes and relationships so it is safe to run repeatedly:
```cypher
MERGE (doc:Document {doc_id: $doc_id}) SET doc.source = $source, ...
MERGE (sec:Section {section_id: $parent_id}) SET sec.section_path = $section_path, ...
MERGE (sec)-[:FROM_DOCUMENT]->(doc)
MERGE (ch:EvidenceChunk {chunk_id: $chunk_id}) SET ch.chunk_content_hash = $chunk_content_hash, ...
MERGE (ch)-[:PART_OF]->(sec)
MERGE (cls:DrugClass {id: $class_id}) SET cls.name = $class_name
MERGE (ctx:ClinicalContext {id: $context_id}) SET ctx.name = $context_name
MERGE (cls)-[r:AVOID_IN {assertion_id: $assertion_id, corpus_release: $corpus_release}]->(ctx)
  SET r.source_chunk_id = $chunk_id, r.rationale = $rationale, ...
MERGE (cls)-[s:SUPPORTED_BY {assertion_id: $assertion_id, corpus_release: $corpus_release}]->(ch)
UNWIND $drug_members AS dm
  MERGE (d:Drug {id: dm.id}) SET d.name = dm.name, d.aliases = dm.aliases
  MERGE (d)-[:MEMBER_OF]->(cls)
```
The resulting graph has nodes: `Document → Section → EvidenceChunk`, `DrugClass ← Drug`, `ClinicalContext`; and edges: `AVOID_IN`, `SUPPORTED_BY`, `PART_OF`, `FROM_DOCUMENT`, `MEMBER_OF`.

**Stale edge pruning:**
```cypher
MATCH ()-[r:AVOID_IN]->()
WHERE r.corpus_release IS NULL OR r.corpus_release <> $corpus_release
   OR NOT r.assertion_id IN $active_assertion_ids
DELETE r
```
Removes any `AVOID_IN` or `SUPPORTED_BY` edges from previous releases or removed assertions, keeping the graph in sync with the current compiled policy.

**Safety guards before Neo4j write:**
```python
for item in compiled_assertions:
    if item.get("review_status") != "approved":
        raise ValueError(f"Blocked unapproved assertion: {item.get('assertion_id')}")
    if item.get("corpus_release") != CORPUS_RELEASE:
        raise ValueError(...)
    if item.get("relation") != "AVOID_IN":
        raise ValueError("Unsupported relation ... add a dedicated Cypher handler before loading.")
```
Only `AVOID_IN` relations are supported — any other relation type requires a new Cypher handler to be written first.

---

## Cell 25 — Medication Normalization, Retrieval, and Safety Lookup

### Cell Summary
Defines the runtime retrieval layer: `APPROVED_SOURCES` allowlist, `DRUG_NORMALIZATION_MAP` (brand/alias/FDC → canonical ingredients), `extract_and_normalize_drugs()`, `get_jurisdiction_coverage()`, `hybrid_retrieve()`, and `retrieve_with_safety_context()`. Demonstrates with two dengue clinical queries.

### Code Explanation

**`APPROVED_SOURCES` allowlist:**
```python
APPROVED_SOURCES = sorted({
    json.loads(mjson)["source"]
    for (mjson,) in conn.execute("""
        SELECT metadata_json FROM child_chunks
        WHERE review_status = 'approved' AND superseded_by IS NULL
          AND json_extract(metadata_json, '$.corpus_release') = ?
    """, (CORPUS_RELEASE,)).fetchall()
})
```
Dynamically built from the live SQLite state at startup. Used as a Qdrant `MatchAny` filter to ensure retrieval is restricted to approved source URLs.

**`DRUG_NORMALIZATION_MAP`:**
A deterministic lookup table mapping brand names, aliases, and fixed-dose combinations (FDCs) to canonical ingredient lists:
```python
"combiflam": ["ibuprofen", "paracetamol"],  # FDC expands to ALL ingredients
"ecosprin":  ["aspirin"],
"voveran":   ["diclofenac"],
```
Sorted by alias length (longest-first) before matching so `"ibugesic plus"` is matched before `"ibugesic"`.

**`extract_and_normalize_drugs(query_text, extra_terms)`:**
Uses `re.search(rf"\b{re.escape(alias)}\b", q_lower)` for each alias to find whole-word matches, then expands to canonical ingredients. Also detects:
- `mentions_existing_prescription` via `_PRESCRIBED_RE` (matches phrases like "prescribed", "already taking", "low-dose").
- `has_negation_cue` via `_NEGATION_RE` (matches "not taking", "avoid", "do not take", etc.).
Unresolved terms (not in the normalization map) are separately tracked.

**`get_jurisdiction_coverage()`:**
Groups chunk statuses by `doc_id` and returns:
- `"available"` — has approved chunks, no quarantine, no pending figures.
- `"partial_figures_pending"` — has approved prose/tables but some figures still in `pending_review`.
- `"unavailable_quarantined"` — doc is quarantined.
- `"unavailable_pending_review"` — doc has no approved chunks yet.

**`hybrid_retrieve(query_text, limit, max_parent_chars)`:**

1. Encodes query as dense vector (`dense_embedder.embed`) and sparse vector (`sparse_embedder.query_embed`).
2. Runs Qdrant prefetch (top-30 dense, top-30 sparse) + RRF fusion, filtered by `APPROVED_SOURCES`, `review_status='approved'`, `corpus_release=CORPUS_RELEASE`, and `superseded_by IS NULL` (using `IsEmptyCondition`).
3. For each result, runs **five runtime guards** that raise `RuntimeError` if any invariant is violated (unapproved chunk leaked, release mismatch, superseded chunk leaked, untrusted source, incomplete provenance).
4. For each hit, queries SQLite for all sibling chunks in the same parent section, separates `approved` units from `unresolved` (pending/quarantined) objects.
5. Assembles context units without mid-unit slicing: the matched hit is always included; sibling units are added only if they fit within `max_parent_chars` without truncating any unit midway; units that don't fit are tracked in `omitted_unit_ids`.
6. Computes `coverage_status`:
   - `"complete"` — no unresolved objects, no omitted units, no quarantined docs.
   - `"partial"` — any unresolved figures, omitted units, or quarantined jurisdiction docs.
   - `"unavailable"` — zero results.

**`retrieve_with_safety_context(query_text, detected_drugs, limit)`:**
Calls `hybrid_retrieve()` then independently calls `extract_and_normalize_drugs()` and `lookup_medication_policy()` for each normalized ingredient. Returns a unified dict with RAG results, drug analysis, safety rules, and coverage metadata.

---

## Cell 26 — `lookup_medication_policy()` and `verify_chunk_in_sqlite()`

### Cell Summary
Defines `verify_chunk_in_sqlite()` (deep provenance cross-check for a policy chunk) and `lookup_medication_policy()` (the dual-backend — Neo4j primary, local policy JSON fallback — medication safety lookup function). Runs three test cases: a canonical drug name, an Indian brand alias, and an unknown drug.

### Code Explanation

**`verify_chunk_in_sqlite(chunk_id, expected_hash)`:**
```python
row = conn.execute("""
    SELECT doc_id, section_path, page_start, page_end,
           review_status, superseded_by, chunk_content_hash, metadata_json, substr(text, 1, 160)
    FROM child_chunks WHERE chunk_id = ?
""", (chunk_id,)).fetchone()
```
Verifies: chunk exists, is approved, is not superseded, has matching `corpus_release`, and has a confirmed `publication_date`. Optionally compares `chunk_content_hash` against `expected_hash` to detect drift.

**`lookup_medication_policy(drug_term, context="suspected_dengue")`:**

Backend 1 — Neo4j (if `NEO4J_PASSWORD` set):
```cypher
MATCH (d:Drug)-[:MEMBER_OF]->(c:DrugClass)
WHERE toLower(d.id) = $term OR toLower(d.name) = $term
   OR any(a IN coalesce(d.aliases, []) WHERE toLower(a) = $term)
MATCH (c)-[r:AVOID_IN]->(ctx:ClinicalContext {id: $context})
MATCH (c)-[s:SUPPORTED_BY]->(ch:EvidenceChunk {chunk_id: r.source_chunk_id})
      -[:PART_OF]->(sec:Section)-[:FROM_DOCUMENT]->(doc:Document)
WHERE r.review_status = 'approved' AND r.corpus_release = $release
  AND s.assertion_id = r.assertion_id AND s.review_status = 'approved'
  AND ch.review_status = 'approved' AND ch.corpus_release = $release
```
Traverses the full provenance graph: Drug → DrugClass → AVOID_IN → ClinicalContext, with the evidence chain DrugClass → SUPPORTED_BY → EvidenceChunk → Section → Document.

Backend 2 — Local policy JSON fallback:
```python
for rule in rules:
    if rule.get("review_status") != "approved" or ...:
        continue
    for dm in rule["drug_members"]:
        candidates = {dm["id"].lower(), dm["name"].lower(), *(a.lower() for a in dm.get("aliases", []))}
        if term in candidates:
            matches.append({...full provenance fields...})
```

**Post-match validation:**
```python
for m in matches:
    if m.get("reviewed_by") in _INVALID_REVIEWERS:
        raise RuntimeError(f"Fail-closed: matched rule ... lacks clinical sign-off.")
    m.update(verify_chunk_in_sqlite(m["chunk_id"], expected_hash=m.get("chunk_content_hash")))
```
Every matched rule is cross-verified against SQLite before being returned.

**Return statuses:**
- `"avoid_rule_matched"` — at least one verified rule found (the drug should be avoided).
- `"no_reviewed_rule_matched"` — no rule matched; note: this **does not** imply safety. The safety note explicitly states: *"Absence of a reviewed rule does NOT establish medication safety; do not recommend use."*
- `"source_conflict"` — at least one matched rule has `conflict_status = "unresolved_conflict"`; conservative handling and clinician deferral are mandated.
- `"drug_mention_unresolved"` — empty or blank drug term.
- `"policy_unavailable"` — policy JSON file is missing.

---

## Cell 27 — Verification Suite (9 Checks)

### Cell Summary
A comprehensive sanity-check cell that runs 9 independent checks against live stores and prints a `✓ PASS` / `✗ FAIL` / `~ SKIP` summary table. This cell should be run after any HITL decision, policy update, or Qdrant rebuild and must show zero `FAIL` entries before Phase 2 begins.

### Code Explanation

| Check | What it verifies |
|---|---|
| **1a** `vocab_reject` | `validate_registry_entry()` correctly raises on an unknown topic label. |
| **1b** `evidence_reject` | `validate_registry_entry()` correctly raises on a document-type string as `evidence_level`. |
| **2** `retrieval_completeness` | `hybrid_retrieve()` source code contains `IsEmptyCondition` and `unresolved_in_section` (proving superseded-chunk filtering and completeness reporting are present). |
| **3** `qdrant_active_parity` | Qdrant has 0 superseded points AND total point count equals SQLite active approved count. |
| **4** `fig_reviewed_at` | All unapproved figure chunks have `reviewed_at = NULL` (approved timestamp must not exist on unapproved content). |
| **5a** `list_markers` | At least one prose chunk in SQLite contains `• ` (bullet markers preserved). |
| **5b** `table_footnotes` | At least one table chunk in SQLite contains `[footnote]` text. |
| **6** `unique_ids` | All `chunk_id` values are unique and are valid UUID5 strings (`uuid.UUID(cid).version == 5`). |
| **7** `quarantine_exclusion` | Quarantined doc chunks have zero points in Qdrant; no unapproved content is indexed. |
| **8** `release_sync` | Full `check_release_sync()` passes (ID/hash parity across SQLite, Qdrant, manifest, and policy). |
| **9** `clinical_signoff` | Policy file exists, every rule has a named reviewer, and `PINNED_NSAID_CHUNK_ID` is set (not `None`). |

```python
print("\n" + "=" * 76)
print("VERIFICATION SUMMARY")
print("=" * 76)
for key, val in results.items():
    icon = "✓" if val.startswith("PASS") else ("~" if val.startswith("SKIP") else "✗")
    print(f"  {icon}  [{key}]  {val}")
```

---

# **Next Parts To Do**

1. **Execute Human-in-the-Loop (HITL) Content Review on Figures and Documents**
   - Run `approve_document_text_and_tables(...)` with your named `reviewer_id` and `rationale` for documents whose ISO `publication_date` is verified, confirming that `prose` and `table` chunks become `approved` while figures move only to `pending_review` (never auto-approved).
   - Call `list_pending_figures()` to enumerate all `pending_review` and `corrected_pending_review` figure chunks in the active `CORPUS_RELEASE`.
   - Inspect each clinical diagram, algorithm, or table-figure one by one using `inspect_figure(chunk_id)` to compare the original image crop, section path, page range, current text, and prior audit events.
   - For each figure, call `record_figure_decision(...)` with a real `reviewer_id` and clear `rationale`: use `'approve'` only when verified accurate, `'reject'` with a specific `rejection_reason` when unusable/erroneous, or `'correct'` with `corrected_text` to log a new hashed entry in `derived_artifacts` (`corrected_pending_review`), then re-inspect and explicitly `'approve'` the corrected artifact before release promotion.

2. **Verify and Resolve NCVBDC (2023) Quarantine Metadata**
   - Inspect the NCVBDC India dengue guideline source record and PDF metadata to confirm its exact ISO `publication_date` (`YYYY-MM-DD`), official source URL/version, jurisdiction (`IN`), document type, and license terms from an authoritative source.
   - Keep `ncvbdc_dengue_guideline_2023` quarantined until its metadata is verified; once verified, update the registry/metadata, re-run ingestion/approval with an audit rationale, and verify how `get_jurisdiction_coverage()` and `coverage_status` reflect India guideline availability.

3. **Pin Reviewed Clinical Assertions and Expand Scoped Policy Rules**
   - Use `find_approved_chunks(...)` to locate and read the exact approved guideline passage supporting dengue NSAID avoidance (and verify page numbers, section path, and context).
   - Set `PINNED_NSAID_CHUNK_ID` and `CLINICAL_REVIEWER_ID` in Cell 23 (removing any `None` or placeholder values), run compilation to generate `safety_policy_{CORPUS_RELEASE}.json`, and confirm Check 9 in Cell 27 passes.
   - Expand `REVIEWED_ASSERTIONS_SPEC` and the policy schema beyond a single `AVOID_IN` rule to cover additional dengue clinical rules (such as warning signs/escalation triggers, diagnostic test windows by illness day, disease phases, patient modifiers like pregnancy/pediatrics/existing prescriptions, and explicit `conflict_status` handling when guidelines differ).

4. **Harden Medication Normalization and Retrieval Completeness Behavior**
   - Expand `DRUG_NORMALIZATION_MAP` with clinically reviewed aliases, regional/Indian brand names, fixed-dose combinations (FDCs), and common spelling/transliteration variants, mapping every multi-ingredient product to all constituent ingredients.
   - Test `retrieve_with_safety_context()` and `lookup_medication_policy()` across edge cases: single vs. combination products, negated mentions, existing prescriptions, unknown/ambiguous drug terms (`drug_mention_unresolved`), and `no_reviewed_rule_matched` responses (verifying no response ever implies clearance or safety).
   - Inspect `coverage_status`, `unresolved_required_objects`, `truncation_occurred`, and `omitted_unit_ids` on real queries involving clinical flowcharts/tables and multi-unit sections so downstream consumers handle incomplete evidence explicitly.

5. **Promote the Verified Release and Run Full Cross-Store Verification**
   - Run Cell 21 to build `guarddengue_{CORPUS_RELEASE}`, prune stale points, verify point parity, and promote the `release_manifests` entry to `'active'` (and run Cell 24 if Neo4j is actively used in your environment).
   - Run Cell 22 (`check_release_sync()`) and Cell 27 (Verification Suite) after any approval, correction, or policy update, confirming zero `FAIL` checks and exact ID/hash alignment across SQLite, Qdrant, `release_manifests`, and `safety_policy_{CORPUS_RELEASE}.json`.

6. **Prepare Phase 2 Generation Contracts, Guardrails, and Evaluation Harness**
   - Before connecting any LLM or SLM generator, define a strict output contract requiring every clinical claim to cite verified `doc_id`, `section_path`, `page`, and `chunk_id`/`assertion_id`, and enforce deterministic abstention or safe fallback templates whenever `coverage_status != "complete"`, required figures/tables are unresolved, or medication lookup is unresolved/conflicted.
   - Build a clinician-reviewed evaluation dataset covering retrieval recall/precision on tables and timelines, Indian brand/FDC normalization, negation/prescription nuance, red-flag escalation, unsupported/ambiguous queries, and store failure/staleness scenarios, and set pass/fail thresholds prior to Phase 2 integration.
