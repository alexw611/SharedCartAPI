from fastapi import APIRouter, Depends, HTTPException, status, Request, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from API.database import get_db
from API.models.user import User
from API.schemas.user import UserCreate, UserLogin, UserResponse
from API.schemas.auth import TokenResponse, TokenRefreshRequest
from API.auth.password import hash_password, verify_password
from API.auth.jwt_handler import create_access_token, create_refresh_token, verify_token
from API.auth.blacklist import add_to_blacklist
from API.rate_limiter import limiter

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "schema": UserCreate.model_json_schema()
                }
            },
            "required": True
        }
    }
)
@limiter.limit("5/minute")
async def register(request: Request, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        body = await request.json()
        user_data = UserCreate(**body)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid data format or missing fields"
        )

    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    new_user = User(
        username=user_data.username,
        displayName=user_data.displayName,
        passwordHash=hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get tokens."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.passwordHash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id)
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
def refresh_token(request: Request, token_request: TokenRefreshRequest, db: Session = Depends(get_db)):
    """Refresh access token."""
    user_id = verify_token(token_request.refresh_token, "refresh")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id)
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
def logout(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and invalidate the current token."""
    token = credentials.credentials
    add_to_blacklist(token)
