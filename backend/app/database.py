from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import get_config

cfg = get_config()
database_url = cfg.SQLALCHEMY_DATABASE_URI
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    database_url,
    **getattr(cfg, "SQLALCHEMY_ENGINE_OPTIONS", {})
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """FastAPI Dependency providing a scoped database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
