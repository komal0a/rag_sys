import jwt
import time
from typing import Dict, Any
from app.core.config import settings


def create_access_token(subject: Dict[str, Any], expires_in: int | None = None) -> str:
    if expires_in is None:
        expires_in = settings.JWT_EXPIRES_IN
    now = int(time.time())
    payload = dict(subject)
    payload.update({"iat": now, "exp": now + int(expires_in)})
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except Exception:
        raise ValueError("Invalid token")
