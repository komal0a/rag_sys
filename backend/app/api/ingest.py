import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.deps import get_db, security
from app.core.jwt import decode_access_token
from app import models
from app.services.extraction import try_extract
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embeddings

router = APIRouter()


@router.post("/ingest/{document_id}", tags=["ingest"])
def ingest_document(document_id: int, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Depends(security)):
    # Decode token locally to avoid cross-dependency DB session issues
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_access_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Fetch document by id and verify ownership
    doc = db.get(models.Document, document_id)
    if not doc or str(doc.user_id) != str(user_id):
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=400, detail="File not found on disk")

    # extract text
    text = try_extract(doc.file_path)
    if not text:
        raise HTTPException(status_code=400, detail="No extractable text found")

    # chunk
    chunks = chunk_text(text)
    if not chunks:
        raise HTTPException(status_code=500, detail="Chunking produced no output")

    # embeddings
    embeddings = generate_embeddings(chunks)

    # persist chunks
    for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
        dc = models.DocumentChunk(document_id=doc.id, chunk_index=idx, content=chunk, embedding=emb)
        db.add(dc)

    doc.status = "processed"
    db.commit()
    return {"document_id": doc.id, "chunks": len(chunks)}
