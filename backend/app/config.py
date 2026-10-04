"""
Configuration classes.
Selected via FLASK_ENV environment variable.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# Ensure outbound connections (Supabase, Gemini, Cloudinary) succeed even if
# the local network adapter's DHCP DNS server fails to resolve external hostnames.
try:
    import socket
    import dns.resolver

    _orig_getaddrinfo = socket.getaddrinfo
    _resolver = dns.resolver.Resolver(configure=False)
    _resolver.nameservers = ["8.8.8.8", "1.1.1.1"]
    _resolver.timeout = 3.0
    _resolver.lifetime = 5.0

    def _fallback_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        try:
            return _orig_getaddrinfo(host, port, family, type, proto, flags)
        except socket.gaierror:
            if isinstance(host, str) and not host.replace(".", "").isdigit():
                try:
                    answers = _resolver.resolve(host, "A")
                    ip = answers[0].to_text()
                    return _orig_getaddrinfo(ip, port, family, type, proto, flags)
                except Exception:
                    pass
            raise

    socket.getaddrinfo = _fallback_getaddrinfo
except Exception:
    pass


class BaseConfig:
    # ── Core ──────────────────────────────────────────────────────────────
    DEBUG: bool = False
    TESTING: bool = False

    # ── Database ──────────────────────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL", "postgresql://localhost/talentforge"
    )
    # Supabase connection strings sometimes use "postgres://" — fix for SQLAlchemy
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )
    if "aws-1-ap-northeast-1.pooler.supabase.com" in SQLALCHEMY_DATABASE_URI and "hostaddr=" not in SQLALCHEMY_DATABASE_URI:
        sep = "&" if "?" in SQLALCHEMY_DATABASE_URI else "?"
        SQLALCHEMY_DATABASE_URI = f"{SQLALCHEMY_DATABASE_URI}{sep}hostaddr=57.182.231.186"
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict = {
        "pool_pre_ping": True,          # reconnect on dropped connections
        "pool_size": 5,
        "max_overflow": 10,
    }

    # ── JWT ───────────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # ── Supabase Auth (Google OAuth) ────────────────────────────────────────
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_JWT_AUDIENCE: str = os.getenv("SUPABASE_JWT_AUDIENCE", "authenticated")

    # ── Cloudinary ────────────────────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

    # ── CORS ──────────────────────────────────────────────────────────────
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # ── Pagination ────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


class ProductionConfig(BaseConfig):
    DEBUG = False
    # Tighten pool for Render's free tier
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_size": 3,
        "max_overflow": 5,
        "pool_timeout": 30,
    }


_config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config():
    env = os.getenv("FLASK_ENV", "development").lower()
    return _config_map.get(env, DevelopmentConfig)
