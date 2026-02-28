from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

from API.config import settings


def create_access_token(user_id: int) -> str:
    """Create a new access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: int) -> str:
    """Create a new refresh token."""
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, token_type: str = "access") -> Optional[int]:
    """Verify a token and return user_id if valid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        
        if payload.get("type") != token_type:
            return None
        
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        return int(user_id)
    except JWTError:
        return None
