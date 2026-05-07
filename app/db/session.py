from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


settings = get_settings()
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    poolclass=(NullPool if settings.db_disable_pooling else None),
    pool_size=None if settings.db_disable_pooling else settings.db_pool_size,
    max_overflow=None if settings.db_disable_pooling else settings.db_max_overflow,
    pool_timeout=None if settings.db_disable_pooling else settings.db_pool_timeout_s,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
