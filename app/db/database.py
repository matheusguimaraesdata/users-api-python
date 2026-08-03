from sqlmodel import SQLModel, Session, create_engine

from app.core.config import settings

connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(settings.DATABASE_URL, echo=False, connect_args=connect_args)


def init_db() -> None:
    """Cria as tabelas no banco caso ainda não existam."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency do FastAPI: entrega uma sessão de banco por requisição."""
    with Session(engine) as session:
        yield session
