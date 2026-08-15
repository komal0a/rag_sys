from __future__ import annotations

import time
from typing import List, Optional, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.services.embeddings import get_provider, EMBEDDING_DIM
from app import models
from app.core.config import settings


class Retriever:
    def __init__(self, db: Session):
        self.db = db
        self.provider = get_provider()

    def embed_query(self, query: str) -> List[float]:
        t0 = time.time()
        vec = self.provider.embed_texts([query])[0]
        self._embed_latency = time.time() - t0
        return vec

    def retrieve(self, query: str, top_k: int | None = None, similarity_threshold: Optional[float] = None, document_id: Optional[int] = None, user_id: Optional[int] = None) -> Dict[str, Any]:
        """Return top-k chunks for `query` filtered by optional document_id and/or user_id.

        If a Postgres+pgvector backend is available the query uses SQL vector operators.
        Otherwise, it falls back to loading JSON embeddings into Python and
        computing cosine similarity with the provider embeddings (used for tests).
        """
        qemb = self.embed_query(query)
        if top_k is None:
            top_k = settings.DEFAULT_TOP_K
        if similarity_threshold is None:
            similarity_threshold = settings.RETRIEVAL_SIMILARITY_THRESHOLD

        # Attempt Postgres vector search if pgvector is available
        try:
            # Use Postgres `vector` operator: <-> for Euclidean, <=> for cosine
            # We will use cosine distance via the `<=>` operator if available.
            sql = "SELECT id, document_id, content, page_number, embedding <=> :qemb AS distance FROM document_chunks"
            where_clauses = []
            params = {"qemb": qemb}
            if document_id:
                where_clauses.append("document_id = :document_id")
                params["document_id"] = document_id
            if user_id:
                # join documents to enforce ownership
                sql = "SELECT dc.id, dc.document_id, dc.content, dc.page_number, dc.embedding <=> :qemb AS distance FROM document_chunks dc JOIN documents d ON dc.document_id = d.id"
                where_clauses.append("d.user_id = :user_id")
                params["user_id"] = user_id
            if where_clauses:
                sql += " WHERE " + " AND ".join(where_clauses)
            sql += " ORDER BY distance LIMIT :k"
            params["k"] = top_k
            res = self.db.execute(text(sql), params).fetchall()
            results = []
            for row in res:
                # distance is a postgres float distance; convert to similarity
                distance = float(row[4])
                similarity = 1.0 - distance
                if similarity >= similarity_threshold:
                    results.append({"chunk_id": int(row[0]), "document_id": int(row[1]), "content": row[2], "page_number": row[3], "similarity": similarity})
            return {"query": query, "results": results, "timings": {"embed": getattr(self, "_embed_latency", None)}}
        except Exception:
            # Fallback: load embeddings into Python and do cosine similarity
            # Note: this is only for test environments without pgvector.
            from math import sqrt

            chunks = self.db.query(models.DocumentChunk).all()
            # Build list of (chunk, emb)
            items = []
            for c in chunks:
                if document_id and c.document_id != document_id:
                    continue
                if user_id:
                    # fetch parent document owner
                    if c.document and c.document.user_id != user_id:
                        continue
                emb = c.embedding
                if not emb:
                    continue
                items.append((c, emb))

            def cosine(a, b):
                da = sum(x * x for x in a) ** 0.5
                db = sum(x * x for x in b) ** 0.5
                if da == 0 or db == 0:
                    return 0.0
                return sum(x * y for x, y in zip(a, b)) / (da * db)

            scored = []
            for c, emb in items:
                sim = cosine(qemb, emb)
                scored.append((sim, c))
            scored.sort(key=lambda x: x[0], reverse=True)
            results = []
            for sim, c in scored[:top_k]:
                if sim >= similarity_threshold:
                    results.append({"chunk_id": c.id, "document_id": c.document_id, "content": c.content, "page_number": c.page_number, "similarity": float(sim)})
            return {"query": query, "results": results, "timings": {"embed": getattr(self, "_embed_latency", None)}}
