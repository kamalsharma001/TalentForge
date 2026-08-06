import datetime
import jwt as pyjwt
from app.config import get_config

def create_access_token(identity: str, expires_delta=None) -> str:
    """Generate a signed JWT access token for a given user identity."""
    cfg = get_config()
    secret_key = cfg.JWT_SECRET_KEY
    if expires_delta is None:
        expires_delta = cfg.JWT_ACCESS_TOKEN_EXPIRES
    
    payload = {
        "sub": str(identity),
        "type": "access",
        "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta
    }
    return pyjwt.encode(payload, secret_key, algorithm="HS256")

def create_refresh_token(identity: str, expires_delta=None) -> str:
    """Generate a signed JWT refresh token for a given user identity."""
    cfg = get_config()
    secret_key = cfg.JWT_SECRET_KEY
    if expires_delta is None:
        expires_delta = cfg.JWT_REFRESH_TOKEN_EXPIRES
    
    payload = {
        "sub": str(identity),
        "type": "refresh",
        "exp": datetime.datetime.now(datetime.timezone.utc) + expires_delta
    }
    return pyjwt.encode(payload, secret_key, algorithm="HS256")
