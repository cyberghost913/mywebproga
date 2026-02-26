from argon2 import PasswordHasher
import hashlib
import os
from datetime import datetime, timezone, timedelta
from .security import ACCESS_TOKEN_LIFETIME, TOKEN_SECRET, TOKEN_ALGORITHM
import jwt
from fastapi.encoders import jsonable_encoder
from .schemas import TokenPayload

ph = PasswordHasher()

def hash_password(password: str) -> str:
    return ph.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        ph.verify(hashed_password, password)
        return True
    except Exception:
        return False

def create_refresh_token() -> str:
    return hashlib.sha256(os.urandom(32)).hexdigest()

def create_access_token(username: str, is_admin: bool, is_author: bool, id: int) -> str:
    payload = TokenPayload(
        username=username,
        is_admin=is_admin,
        is_author=is_author,
        id=id,
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_LIFETIME)
    )
    payload_dict = payload.model_dump(mode='json')
    return jwt.encode(jsonable_encoder(payload_dict), TOKEN_SECRET, algorithm=TOKEN_ALGORITHM)