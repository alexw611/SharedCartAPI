from pydantic import BaseModel, field_validator
from typing import Optional
import re


def validate_password_strength(v: str) -> str:
    """Validate password strength rules."""
    if len(v) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", v):
        raise ValueError('Password must contain at least one special character')
    return v


class UserBase(BaseModel):
    username: str
    displayName: str


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserUpdate(BaseModel):
    displayName: str


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class PasswordChange(BaseModel):
    oldPassword: str
    newPassword: str

    @field_validator('newPassword')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)
