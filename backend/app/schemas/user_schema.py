from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.utils.validators import validate_password_strength

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    role: str
    first_name: str
    last_name: str
    full_name: str
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserRegistrationSchema(BaseModel):
    email: EmailStr
    password: str
    role: str
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None

    @field_validator("email", mode="before")
    @classmethod
    def strip_email(cls, v):
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("first_name", "last_name", mode="before")
    @classmethod
    def strip_spaces(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("password")
    @classmethod
    def validate_pwd(cls, v):
        error = validate_password_strength(v)
        if error:
            raise ValueError(error)
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ("recruiter", "interviewer", "candidate"):
            raise ValueError("Role must be recruiter, interviewer, or candidate")
        return v

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class OAuthGoogleStartSchema(BaseModel):
    supabase_access_token: str

class OAuthGoogleCompleteSchema(BaseModel):
    supabase_access_token: str
    role: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v not in ("recruiter", "interviewer", "candidate"):
            raise ValueError("Role must be recruiter, interviewer, or candidate")
        return v

class UserUpdateSchema(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
