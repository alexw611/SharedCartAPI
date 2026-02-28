from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from API.database import get_db
from API.models.user import User
from API.schemas.user import UserResponse, UserUpdate, PasswordChange
from API.auth.dependencies import get_current_user
from API.auth.password import verify_password, hash_password
from API.rate_limiter import limiter

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
@limiter.limit("120/minute")
def get_my_profile(request: Request, current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
@limiter.limit("30/minute")
def update_profile(
    request: Request,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    current_user.displayName = user_data.displayName
    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def change_password(
    request: Request,
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password."""
    if not verify_password(password_data.oldPassword, current_user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong password"
        )
    
    current_user.passwordHash = hash_password(password_data.newPassword)
    db.commit()


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete_my_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user account."""
    db.delete(current_user)
    db.commit()


@router.get("/search", response_model=List[UserResponse])
@limiter.limit("60/minute")
def search_users(
    request: Request,
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search users by username."""
    if len(query) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query must be at least 2 characters"
        )
    
    users = db.query(User).filter(
        User.username.contains(query),
        User.id != current_user.id
    ).limit(10).all()
    
    return users
