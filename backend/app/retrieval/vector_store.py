"""
GuardDengue — Qdrant Vector Store Adapter (Zone 4)

Connects to embedded local Qdrant collection (guarddengue_v0.1-dev).
Executes vector similarity search with metadata filtering (approved chunks only).
"""
import logging
from typing import Any, Literal
import numpy as np
from qdrant_client import QdrantClient, models

from app.core.config import settings
from app.retrieval.embeddings import get_dense_embedding, get_sparse_bm25_embedding

logger = logging.getLogger("guarddengue.retrieval.vector")

class VectorStore:
    def __init__(
        self,
        storage_dir: str | None = None,
        corpus_release: str | None = None,
        collection_name: str | None = None
    ):
        self.storage_dir = storage_dir or str(settings.QDRANT_STORAGE_DIR)
        self.corpus_release = corpus_release or settings.CORPUS_RELEASE
        self.collection_name = collection_name or getattr(settings, "QDRANT_COLLECTION", f"guarddengue_{self.corpus_release}")
        self.client = QdrantClient(path=self.storage_dir)
        self._verified_collections: set[str] = set()

    def search(
        self,
        query: str,
        top_k: int = 5,
        topic: str | None = None,
        score_threshold: float = 0.2,
        retrieval_mode: Literal["dense", "hybrid"] | None = None,
        prefetch_limit: int | None = None,
        collection_name: str | None = None,
        dense_oos_floor: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Searches Qdrant for guideline chunks matching the citizen query.
        Supports isolated 'dense' (cosine) and 'hybrid' (dense + Qdrant/bm25 RRF fusion) modes.
        Filters by corpus_release and review_status == 'approved'.
        """
        target_collection = collection_name or self.collection_name
        active_mode = retrieval_mode or getattr(settings, "RETRIEVAL_MODE", "dense")
        active_prefetch = prefetch_limit or getattr(settings, "HYBRID_PREFETCH_LIMIT", 20)

        if target_collection not in self._verified_collections:
            if not self.client.collection_exists(target_collection):
                logger.warning(f"Qdrant collection {target_collection} does not exist.")
                return []
            self._verified_collections.add(target_collection)

        dense_vector = get_dense_embedding(query, dim=384)

        # Build payload filters: approved review status, no superseded chunks
        filter_conditions = [
            models.FieldCondition(
                key="review_status",
                match=models.MatchValue(value="approved")
            )
        ]
        if topic:
            filter_conditions.append(
                models.FieldCondition(
                    key="topic",
                    match=models.MatchValue(value=topic)
                )
            )

        query_filter = models.Filter(must=filter_conditions)

        if active_mode == "hybrid":
            sparse_vec_dict = get_sparse_bm25_embedding(query, is_query=True)
            sparse_vector = models.SparseVector(
                indices=sparse_vec_dict["indices"],
                values=sparse_vec_dict["values"],
            )
            results = self.client.query_points(
                collection_name=target_collection,
                prefetch=[
                    models.Prefetch(
                        query=dense_vector,
                        using="dense",
                        filter=query_filter,
                        limit=active_prefetch,
                    ),
                    models.Prefetch(
                        query=sparse_vector,
                        using="sparse",
                        filter=query_filter,
                        limit=active_prefetch,
                    ),
                ],
                query=models.FusionQuery(fusion=models.Fusion.RRF),
                limit=top_k,
                with_payload=True,
                with_vectors=["dense"],
            )
            hits = results.points

            # Enforce OOS abstention via exact dense cosine dot product on fused top-k candidates
            effective_oos_floor = (
                dense_oos_floor
                if dense_oos_floor is not None
                else getattr(settings, "HYBRID_DENSE_OOS_FLOOR", score_threshold)
            )
            if hits and effective_oos_floor > 0.0:
                qd_np = np.asarray(dense_vector, dtype=np.float32)
                max_dense_cos = max(
                    (
                        float(np.dot(qd_np, np.asarray(h.vector["dense"], dtype=np.float32)))
                        for h in hits
                        if isinstance(getattr(h, "vector", None), dict) and h.vector.get("dense")
                    ),
                    default=0.0,
                )
                if max_dense_cos < effective_oos_floor:
                    return []
        else:
            try:
                # Query points using named vector "dense"
                results = self.client.query_points(
                    collection_name=target_collection,
                    query=dense_vector,
                    using="dense",
                    query_filter=query_filter,
                    limit=top_k,
                    score_threshold=score_threshold
                )
                hits = results.points
            except Exception as e:
                logger.info(f"query_points failed ({e}); falling back to client.search")
                try:
                    hits = self.client.search(
                        collection_name=target_collection,
                        query_vector=("dense", dense_vector),
                        query_filter=query_filter,
                        limit=top_k,
                        score_threshold=score_threshold
                    )
                except Exception as ex:
                    logger.error(f"Vector search failed completely: {ex}")
                    return []

        formatted_hits = []
        for hit in hits:
            formatted_hits.append({
                "id": str(hit.id),
                "score": float(hit.score),
                "payload": hit.payload or {}
            })

        return formatted_hits

    def close(self):
        """Closes embedded Qdrant client cleanly to release flock without teardown races."""
        if hasattr(self, "client") and self.client is not None:
            try:
                self.client.close()
            except Exception:
                pass
            if hasattr(self.client, "_client"):
                try:
                    del self.client._client
                except AttributeError:
                    pass

import atexit
# Singleton instance
vector_store = VectorStore()
atexit.register(vector_store.close)
