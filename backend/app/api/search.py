from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.services.retrieval import Retriever

router = APIRouter()


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: Optional[int] = Field(5, ge=1, le=50)
    document_id: Optional[int] = None


@router.post('/documents/search')
def search(req: SearchRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    retriever = Retriever(db)
    res = retriever.retrieve(req.query, top_k=req.top_k, document_id=req.document_id, user_id=current_user.id)
    return res
