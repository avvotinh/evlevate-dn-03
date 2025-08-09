from typing import List, Dict, Optional
import logging

try:
    from pinecone import Pinecone, ServerlessSpec
except ImportError as e:  # pragma: no cover
    Pinecone = None  # type: ignore
    ServerlessSpec = None  # type: ignore
    logging.warning("pinecone package not available: %s. Install with: pip install pinecone", e)

from src.config.config import (
    PINECONE_API_KEY,
    PINECONE_INDEX_NAME,
    PINECONE_DIMENSION,
    PINECONE_METRIC,
    PINECONE_CLOUD,
    PINECONE_REGION,
)


class VectorDB:
    """Minimal Pinecone wrapper for index init, upsert, query, and update."""

    def __init__(self) -> None:
        if not PINECONE_API_KEY or Pinecone is None:
            raise RuntimeError("Pinecone not configured. Install pinecone-client and set PINECONE_API_KEY.")
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = PINECONE_INDEX_NAME
        self._ensure_index()
        self.index = self.pc.Index(self.index_name)

    def _ensure_index(self) -> None:
        existing = {i["name"] for i in self.pc.list_indexes()}
        if self.index_name not in existing:
            if ServerlessSpec is None:
                raise RuntimeError("pinecone ServerlessSpec not available. Update pinecone-client to >=3.0.0")
            logging.info("Creating Pinecone index '%s'...", self.index_name)
            self.pc.create_index(
                name=self.index_name,
                dimension=PINECONE_DIMENSION,
                metric=PINECONE_METRIC,
                spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION),
            )

    def upsert(self, ids: List[str], vectors: List[List[float]], metadatas: Optional[List[Dict]] = None) -> Dict:
        items = []
        for i, v in zip(ids, vectors):
            item = {"id": i, "values": v}
            items.append(item)
        if metadatas:
            for item, md in zip(items, metadatas):
                item["metadata"] = md
        return self.index.upsert(vectors=items)

    def query(self, vector: List[float], top_k: int = 5, include_metadata: bool = True) -> Dict:
        return self.index.query(vector=vector, top_k=top_k, include_metadata=include_metadata)

    def update(self, _id: str, vector: Optional[List[float]] = None, set_metadata: Optional[Dict] = None) -> Dict:
        return self.index.update(id=_id, values=vector, set_metadata=set_metadata)

    def fetch(self, ids: List[str]) -> Dict:
        """Fetch vectors by IDs"""
        return self.index.fetch(ids=ids)

    def list_stats(self) -> Dict:
        """Get index statistics"""
        return self.index.describe_index_stats()

    def delete(self, ids: List[str]) -> Dict:
        """Delete vectors by IDs"""
        return self.index.delete(ids=ids)
