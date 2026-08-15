from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.deps import get_db
from app import models
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token

router = APIRouter()


class RegisterPayload(BaseModel):
    email: str
    password: str


class LoginPayload(BaseModel):
    email: str
    password: str


@router.post("/register", response_model=dict)
def register(payload: RegisterPayload, db: Session = Depends(get_db)):
    if not payload.email or not payload.password or len(payload.password) < 6:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hp = hash_password(payload.password)
    user = models.User(email=payload.email, hashed_password=hp)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email}


@router.post("/login", response_model=dict)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=dict)
def me(current_user=Depends(lambda: None)):
    # This route will be overridden by dependency injection in tests if needed.
    return {"detail": "noop"}
