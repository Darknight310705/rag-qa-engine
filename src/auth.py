"""
JWT-based authentication: password hashing, access + refresh token
issuance and verification. Uses an in-memory user store for demo
purposes -- swap `USERS` for a real database table in production.
"""
import datetime
from typing import Optional

import jwt
from passlib.context import CryptContext

from src.config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_MINUTES, JWT_REFRESH_EXPIRY_DAYS

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Demo in-memory user store: {username: hashed_password}
# In production this is a users table, and signup would insert into it.
USERS = {
    "demo": pwd_context.hash("demo1234"),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str) -> bool:
    hashed = USERS.get(username)
    if not hashed:
        return False
    return verify_password(password, hashed)


def create_access_token(username: str) -> str:
    payload = {
        "sub": username,
        "type": "access",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=JWT_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(username: str) -> str:
    payload = {
        "sub": username,
        "type": "refresh",
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=JWT_REFRESH_EXPIRY_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
