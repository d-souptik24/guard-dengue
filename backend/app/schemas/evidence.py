"""
GuardDengue — Evidence Data Contracts

Mirrors the 4-field metadata contract from Plan Version 2 and frontend/src/types/index.ts.
"""
from typing import Any
from pydantic import BaseModel, Field

class EvidenceMetadata(BaseModel):
    """Authoritative metadata attached to every retrieved evidence chunk."""
    source: str = Field(..., description="Canonical publisher, e.g. WHO Guidelines 2024, ICMR")
    publication_date: str = Field(..., description="ISO 8601 date: YYYY-MM-DD")
    evidence_level: str = Field(
        ...,
        description="Controlled GRADE level, e.g. Level 1 (Global Clinical Practice Guideline)"
    )
    topic: list[str] | str = Field(..., description="Labels from the 13-category taxonomy")
    chunk_id: str | None = Field(default=None, description="Deterministic chunk identifier")
    review_status: str | None = Field(default="approved", description="approved | pending | quarantined")
    corpus_release: str | None = Field(default="v0.1-dev", description="Corpus release tag")
    section_path: str | None = Field(default=None, description="Document section hierarchy")
    page_start: int | None = Field(default=None, description="Starting page number")
    page_end: int | None = Field(default=None, description="Ending page number")

class EvidenceChunk(BaseModel):
    """A retrieved knowledge chunk from Qdrant and SQLite."""
    id: str
    score: float = Field(default=1.0, description="Cosine similarity or RRF fusion score")
    category: str = Field(default="Dengue basics", description="Primary topic category")
    content: str = Field(..., description="Verbatim text of the guideline passage")
    metadata: EvidenceMetadata
