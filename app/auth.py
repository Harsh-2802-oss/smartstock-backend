import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import models
from .database import get_db

SECRET_KEY = os.getenv("SMARTSTOCK_SECRET", "change-me-in-production")
ALGORITHM = "HS256"
TOKEN_MINUTES = int(os.getenv("SMARTSTOCK_TOKEN_MINUTES", "720"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: int, store_id: int) -> str:
    claims = {
        "sub": str(user_id),
        "store": store_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_MINUTES),
    }
    return jwt.encode(claims, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", {"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = db.get(models.User, int(payload["sub"]))
    except (JWTError, KeyError, ValueError):
        raise error
    if user is None:
        raise error
    return user
