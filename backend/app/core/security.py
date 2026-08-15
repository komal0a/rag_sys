import hashlib
import os
import hmac
from typing import Tuple


def _pbkdf2_hash(password: str, salt: bytes = None, iterations: int = 100_000) -> Tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return salt, dk


def hash_password(password: str) -> str:
    iterations = 100_000
    salt, dk = _pbkdf2_hash(password, iterations=iterations)
    return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iter_s, salt_hex, dk_hex = stored.split("$")
        iterations = int(iter_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(dk_hex)
    except Exception:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(dk, expected)
