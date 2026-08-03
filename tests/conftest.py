import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.db.database import get_session
from app.main import app


@pytest.fixture(name="session")
def session_fixture():
    """Banco SQLite em memória, criado do zero a cada teste (isolamento total)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """TestClient com a dependência get_session substituída pelo banco de teste."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def usuario_payload():
    """Payload padrão válido para criar um usuário nos testes."""
    return {
        "nome": "Usuário de Teste",
        "conta": {"numero": "00099-9", "agencia": "0001", "balanco": 100.0, "limite": 500.0},
        "cartao": {"icone": "https://example.com/icon.svg", "descricao": "Cartão de teste"},
        "recurso": [],
        "news": [],
    }
