from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.deps import get_db
from app import models

router = APIRouter()


class DocumentCreate(BaseModel):
    user_id: int
    filename: str
    num_pages: int | None = None


@router.post("/", response_model=dict)
def create_document(payload: DocumentCreate, db: Session = Depends(get_db)):
    # Verify owner exists
    user = db.query(models.User).filter(models.User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    doc = models.Document(user_id=payload.user_id, filename=payload.filename, num_pages=payload.num_pages)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "filename": doc.filename, "user_id": doc.user_id}


@router.get("/", response_model=list)
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).all()
    return [{"id": d.id, "filename": d.filename, "user_id": d.user_id} for d in docs]
