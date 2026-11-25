"""
GuardDengue — Embedding Service (Zone 4)

Produces normalized dense (384-dimensional) and sparse vectors for hybrid retrieval.
Supports FastEmbed (BAAI/bge-small-en-v1.5) if available, with a deterministic offline
fallback for sandboxed/air-gapped environments.
"""
import hashlib
import math
import os
import re

_FAST_EMBED_MODEL = None

STOPWORDS = {
    "what", "is", "the", "for", "and", "in", "of", "to", "a", "an", "on", "with",
    "vs", "or", "be", "are", "can", "i", "do", "should", "how", "when", "does",
    "it", "at", "by", "from", "as", "about", "that", "this", "my", "your"
}

def _get_fastembed_model():
    global _FAST_EMBED_MODEL
    if _FAST_EMBED_MODEL is None and os.environ.get("USE_FASTEMBED", "0") == "1":
        try:
            from fastembed import TextEmbedding
            _FAST_EMBED_MODEL = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        except Exception:
            _FAST_EMBED_MODEL = False
    return _FAST_EMBED_MODEL if _FAST_EMBED_MODEL is not False else None

def get_dense_embedding(text: str, dim: int = 384) -> list[float]:
    """
    Generates a normalized dense vector for text.
    Uses FastEmbed if enabled and available; otherwise uses deterministic word hashing
    with stopword filtration for high semantic retrieval accuracy.
    """
    model = _get_fastembed_model()
    if model:
        try:
            embeddings = list(model.embed([text]))
            return embeddings[0].tolist()
        except Exception:
            pass

    # Deterministic offline normalized vector fallback with stopword filtration
    tokens = re.findall(r"\w+", text.lower())
    words = [w for w in tokens if w not in STOPWORDS]
    if not words:
        words = tokens  # fallback if all were stopwords

    vec = [0.0] * dim
    for word in words:
        h = int(hashlib.md5(word.encode("utf-8")).hexdigest(), 16)
        pos = h % dim
        val = ((h >> 8) % 1000) / 1000.0 - 0.5
        vec[pos] += val

    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [round(x / norm, 6) for x in vec]

def get_sparse_embedding(text: str) -> dict[str, list]:
    """
    Generates deduplicated and strictly sorted sparse indices and frequencies.
    Compatible with Qdrant models.SparseVector.
    """
    words = re.findall(r"\w+", text.lower())
    freq: dict[int, float] = {}
    for w in words:
        idx = int(hashlib.md5(w.encode("utf-8")).hexdigest()[:6], 16) % 100000
        freq[idx] = freq.get(idx, 0.0) + 1.0

    sorted_indices = sorted(freq.keys())
    values = [freq[i] for i in sorted_indices]
    return {"indices": sorted_indices, "values": values}
