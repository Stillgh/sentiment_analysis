from sqlmodel import create_engine, Session

from config.db_config import get_settings


def create_db_engine():
    settings = get_settings()
    return create_engine(
        url=settings.DATABASE_URL_psycopg,
        echo=False,
        pool_size=5,
        max_overflow=10
    )


_engine = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def get_session():
    engine = get_engine()
    with Session(engine) as session:
        yield session
