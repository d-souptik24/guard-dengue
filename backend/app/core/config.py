"""
GuardDengue — Central Application Settings & Environment Configuration
"""
from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Application identity
    APP_NAME: str = "GuardDengue Backend"
    APP_VERSION: str = "2.0 (Plan v2)"
    DEBUG: bool = False
    
    # Corpus release tag (synchronized with Ayan's Module 2 pipeline)
    CORPUS_RELEASE: str = "v0.1-dev"
    
    # Path resolution (relative to backend root)
    BACKEND_ROOT: Path = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: Path = BACKEND_ROOT / "data"
    STATIC_DIR: Path = BACKEND_ROOT / "static"
    
    # Knowledge pipeline storage paths (prioritizing verified extracted stores)
    KNOWLEDGE_DIR: Path = BACKEND_ROOT / "knowledge_pipeline" / "extracted"
    SQLITE_DB_PATH: Path = (
        KNOWLEDGE_DIR / "guarddengue_chunks.db"
        if (KNOWLEDGE_DIR / "guarddengue_chunks.db").exists()
        else DATA_DIR / "guarddengue_chunks.db"
    )
    QDRANT_STORAGE_DIR: Path = (
        KNOWLEDGE_DIR / "qdrant_local"
        if (KNOWLEDGE_DIR / "qdrant_local").exists()
        else DATA_DIR / "qdrant_storage"
    )
    POLICY_FILE_PATH: Path = (
        KNOWLEDGE_DIR / "safety_policy_v0.1-dev.json"
        if (KNOWLEDGE_DIR / "safety_policy_v0.1-dev.json").exists()
        else DATA_DIR / "safety_policy_v0.1-dev.json"
    )
    QDRANT_COLLECTION: str = "guarddengue_v0.1-dev"
    RETRIEVAL_MODE: Literal["dense", "hybrid"] = "dense"
    HYBRID_PREFETCH_LIMIT: int = 20
    HYBRID_DENSE_OOS_FLOOR: float = 0.67
    
    # Neo4j configuration (optional with automatic local fallback)
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = ""
    
    # Model serving settings
    SLM_PROVIDER: str = "mock"  # "mock" | "local" | "api"
    SLM_MODEL_NAME: str = "Ministral-3B-Medical-v1"
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
