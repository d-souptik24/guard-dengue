"""
GuardDengue — Qdrant Vector Store Adapter (Zone 4)

Connects to embedded local Qdrant collection (guarddengue_v0.1-dev).
Executes vector similarity search with metadata filtering (approved chunks only).
"""
import logging
from typing import Any
from qdrant_client import QdrantClient, models

from app.core.config import settings
from app.retrieval.embeddings import get_dense_embedding

logger = logging.getLogger("guarddengue.retrieval.vector")

class VectorStore:
    def __init__(self, storage_dir: str | None = None, corpus_release: str | None = None):
        self.storage_dir = storage_dir or str(settings.QDRANT_STORAGE_DIR)
        self.corpus_release = corpus_release or settings.CORPUS_RELEASE
        self.collection_name = f"guarddengue_{self.corpus_release}"
        self.client = QdrantClient(path=self.storage_dir)

    def search(
        self,
        query: str,
        top_k: int = 5,
        topic: str | None = None,
        score_threshold: float = 0.2
    ) -> list[dict[str, Any]]:
        """
        Searches Qdrant for guideline chunks matching the citizen query.
        Filters by corpus_release and review_status == 'approved'.
        """
        if not self.client.collection_exists(self.collection_name):
            logger.warning(f"Qdrant collection {self.collection_name} does not exist.")
            return []

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

        try:
            # Query points using named vector "dense"
            results = self.client.query_points(
                collection_name=self.collection_name,
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
                    collection_name=self.collection_name,
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

# Singleton instance
vector_store = VectorStore()
