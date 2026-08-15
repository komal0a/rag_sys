from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
try:
    from pydantic import EmailStr
except Exception:  # pragma: no cover - fallback for environments without email-validator
    EmailStr = str
from app.deps import get_db
from app import models

router = APIRouter()


class UserCreate(BaseModel):
    email: str
    password: str


@router.post("/", response_model=dict)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(email=payload.email, hashed_password=payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.get("/", response_model=list)
def list_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "email": u.email} for u in users]
