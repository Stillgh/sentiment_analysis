from sqlmodel import create_engine, SQLModel, Session

from service.crud.model_service import create_default_model
from service.crud.user_service import create_admin_user
from .config import get_settings

engine = create_engine(url=get_settings().DATABASE_URL_psycopg,
                       echo=True, pool_size=5, max_overflow=10)

def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        create_admin_user(session)
        create_default_model(session)
