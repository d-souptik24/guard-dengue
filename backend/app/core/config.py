"""
GuardDengue — Central Application Settings & Environment Configuration
"""
from pathlib import Path
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
    
    # Storage paths
    SQLITE_DB_PATH: Path = DATA_DIR / "guarddengue_chunks.db"
    QDRANT_STORAGE_DIR: Path = DATA_DIR / "qdrant_storage"
    POLICY_FILE_PATH: Path = DATA_DIR / "safety_policy_v0.1-dev.json"
    
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
