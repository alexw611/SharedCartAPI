from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from API.database import get_db
from API.auth.jwt_handler import verify_token
from API.auth.blacklist import is_blacklisted
from API.models.user import User

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user."""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    user_id = verify_token(token, "access")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
