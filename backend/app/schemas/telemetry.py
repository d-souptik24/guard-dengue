"""
GuardDengue — Observability & Telemetry Schemas
"""
from typing import Any
from pydantic import BaseModel, Field

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    thinking_tokens: int = 0
    total_tokens: int = 0

class GenerationResult(BaseModel):
    text: str
    thinking_trace: str | None = None
    token_usage: TokenUsage = Field(default_factory=TokenUsage)
    latency_ms: float = 0.0

class TraceStep(BaseModel):
    node: str
    status: str
    timestamp: str
    data: dict[str, Any] = Field(default_factory=dict)
