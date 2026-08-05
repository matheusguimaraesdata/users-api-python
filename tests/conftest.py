import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.security import hash_password
from app.db.database import get_session
from app.main import app
from app.models.auth import AuthUser

TEST_USERNAME = "admin"
TEST_PASSWORD = "senha-de-teste"


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
        # usuário de auth fixo para os testes que precisam de token
        session.add(AuthUser(username=TEST_USERNAME, hashed_password=hash_password(TEST_PASSWORD)))
        session.commit()
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """TestClient com a dependência get_session substituída pelo banco de teste.

    Usado para os endpoints públicos (GET). Para endpoints protegidos,
    use a fixture `auth_client`.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_client")
def auth_client_fixture(client: TestClient):
    """Um TestClient SEPARADO (não o mesmo objeto de `client`) já com o header
    Authorization preenchido — usado nos testes de POST/PUT/PATCH/DELETE.

    Precisa ser uma instância própria: se reaproveitássemos `client` e só
    adicionássemos o header nele, os dois fixtures apontariam pro mesmo
    objeto e os testes que checam "sem token" também sairiam autenticados.
    """
    login = client.post(
        "/auth/login", data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    token = login.json()["access_token"]

    authed = TestClient(app)
    authed.headers.update({"Authorization": f"Bearer {token}"})
    return authed


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
