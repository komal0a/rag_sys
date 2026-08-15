from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app import models

router = APIRouter()


class ConversationOut(BaseModel):
    id: int
    title: str | None


@router.post("")
def create_conversation(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    conv = models.Conversation(user_id=current_user.id)
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return {"id": conv.id, "title": conv.title}


@router.get("", response_model=List[ConversationOut])
def list_conversations(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    convs = db.query(models.Conversation).filter(models.Conversation.user_id == current_user.id).all()
    return [{"id": c.id, "title": c.title} for c in convs]


@router.get("/{conv_id}")
def get_conversation(conv_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    messages = db.query(models.Message).filter(models.Message.conversation_id == conv.id).order_by(models.Message.created_at).all()
    return {"id": conv.id, "title": conv.title, "messages": [{"sender": m.sender, "content": m.content, "created_at": m.created_at.isoformat()} for m in messages]}


@router.delete("/{conv_id}")
def delete_conversation(conv_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    conv = db.query(models.Conversation).filter(models.Conversation.id == conv_id).first()
    if not conv or conv.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Conversation not found")
    db.delete(conv)
    db.commit()
    return {"status": "deleted"}
