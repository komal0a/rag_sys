from __future__ import annotations

import os
import traceback
from typing import Optional

from app.database import SessionLocal
from sqlalchemy.orm import Session
from app import models
from app.services.extraction import try_extract
from app.services.chunker import chunk_text
from app.services.embeddings import get_provider


def process_document(document_id: int, user_id: Optional[int] = None, skip_if_processed: bool = True) -> dict:
    db: Session = SessionLocal()
    try:
        doc = db.get(models.Document, document_id)
        if not doc:
            return {"status": "not_found"}
        if user_id is not None and str(doc.user_id) != str(user_id):
            return {"status": "forbidden"}

        # idempotency: if already processed and chunks exist, skip
        existing = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc.id).count()
        if skip_if_processed and existing > 0:
            doc.status = "processed"
            db.commit()
            return {"status": "already_processed", "chunks": existing}

        # check file
        if not doc.file_path or not os.path.exists(doc.file_path):
            doc.status = "failed"
            doc.meta = {"error": "file_missing"}
            db.commit()
            return {"status": "file_missing"}

        text = try_extract(doc.file_path)
        if not text:
            doc.status = "failed"
            doc.meta = {"error": "no_text"}
            db.commit()
            return {"status": "no_text"}

        chunks = chunk_text(text)
        if not chunks:
            doc.status = "failed"
            doc.meta = {"error": "chunk_failure"}
            db.commit()
            return {"status": "chunk_failure"}

        provider = get_provider()
        try:
            embeddings = provider.embed_texts(chunks)
        except Exception as e:
            # embedding failure: do not leave partial chunks
            doc.status = "failed"
            doc.meta = {"error": "embedding_failure", "detail": str(e)}
            db.commit()
            return {"status": "embedding_failure"}

        # remove existing chunks to avoid duplicates (idempotent)
        db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc.id).delete()
        db.commit()

        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            dc = models.DocumentChunk(document_id=doc.id, chunk_index=idx, content=chunk, embedding=emb)
            db.add(dc)

        doc.status = "processed"
        doc.meta = None
        db.commit()
        count = db.query(models.DocumentChunk).filter(models.DocumentChunk.document_id == doc.id).count()
        return {"status": "processed", "chunks": count}
    except Exception:
        db.rollback()
        try:
            doc = db.get(models.Document, document_id)
            if doc:
                doc.status = "failed"
                doc.meta = {"error": "ingest_exception", "trace": traceback.format_exc()}
                db.commit()
        except Exception:
            pass
        return {"status": "error"}
    finally:
        db.close()
