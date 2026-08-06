from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_schema import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserResponse,
    OAuthGoogleStartSchema,
    OAuthGoogleCompleteSchema,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", status_code=201)
def register(data: UserRegistrationSchema, db: Session = Depends(get_db)):
    result = AuthService.register(db, data.model_dump())
    return result

@router.post("/login")
def login(data: UserLoginSchema, db: Session = Depends(get_db)):
    result = AuthService.login(db, data.email, data.password)
    return result

@router.post("/oauth/google")
def oauth_google(data: OAuthGoogleStartSchema, db: Session = Depends(get_db)):
    result = AuthService.oauth_google_start(db, data.supabase_access_token)
    return result

@router.post("/oauth/google/complete", status_code=201)
def oauth_google_complete(data: OAuthGoogleCompleteSchema, db: Session = Depends(get_db)):
    result = AuthService.oauth_google_complete(
        db,
        supabase_access_token=data.supabase_access_token,
        role=data.role,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
    )
    return result

from pydantic import BaseModel
import jwt as pyjwt
from app.config import get_config

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/refresh")
def refresh(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    cfg = get_config()
    secret_key = cfg.JWT_SECRET_KEY
    try:
        payload = pyjwt.decode(body.refresh_token, secret_key, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Valid refresh token required",
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except pyjwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid refresh token: {str(e)}",
        )

    result = AuthService.refresh_token(db, str(user_id))
    return result

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}

@router.post("/change-password")
def change_password(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")
    if not old_password or not new_password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="old_password and new_password are required",
        )
    AuthService.change_password(db, current_user, old_password, new_password)
    return {"message": "Password changed successfully"}
