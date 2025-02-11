from sqlmodel import create_engine, Session

from config.db_config import get_settings

engine = create_engine(url=get_settings().DATABASE_URL_psycopg,
                       echo=True, pool_size=5, max_overflow=10)


def get_session():
    with Session(engine) as session:
        yield session
