from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.deps import get_db, get_current_user
from app import models
from app.core.config import settings
from uuid import uuid4
import os


def _secure_filename(name: str) -> str:
    # simple sanitation: remove path separators and keep only safe chars
    return "".join(c for c in name if c.isalnum() or c in (".", "-", "_"))

router = APIRouter()


class DocumentCreate(BaseModel):
    filename: str
    num_pages: int | None = None


@router.post("/", response_model=dict)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Create document owned by current user
    doc = models.Document(user_id=current_user.id, filename=payload.filename, num_pages=payload.num_pages)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "user_id": doc.user_id}



@router.post("/upload", response_model=dict)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # Validate content type and extension
    filename = file.filename or "upload"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are allowed")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid content type")

    # Size limit (MB)
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    contents = file.file.read()
    size = len(contents)
    if size > max_bytes:
        raise HTTPException(status_code=400, detail="File too large")

    upload_dir = settings.UPLOAD_DIR
    os.makedirs(upload_dir, exist_ok=True)

    stored_name = f"{uuid4().hex}_{_secure_filename(filename)}"
    stored_path = os.path.join(upload_dir, stored_name)
    with open(stored_path, "wb") as fh:
        fh.write(contents)

    doc = models.Document(
        user_id=current_user.id,
        filename=stored_name,
        original_filename=filename,
        file_path=stored_path,
        content_type=file.content_type,
        file_size=size,
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "original_filename": doc.original_filename}


@router.get("/{doc_id}", response_model=dict)
def get_document(doc_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    return {
        "id": doc.id,
        "filename": doc.filename,
        "original_filename": doc.original_filename,
        "file_size": doc.file_size,
        "content_type": doc.content_type,
        "status": doc.status,
    }


@router.delete("/{doc_id}")
def delete_document(doc_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc or doc.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Document not found")
    # delete file
    try:
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
    except Exception:
        pass
    db.delete(doc)
    db.commit()
    return {"status": "deleted"}


@router.get("/", response_model=list)
def list_documents(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    docs = db.query(models.Document).filter(models.Document.user_id == current_user.id).all()
    return [{"id": d.id, "filename": d.filename, "user_id": d.user_id} for d in docs]
