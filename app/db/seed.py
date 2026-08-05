from sqlmodel import Session, select

from app.core.config import settings
from app.core.security import hash_password
from app.models.auth import AuthUser
from app.models.usuario import Cartao, Conta, News, Usuario

ICONE_CREDITO = "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg"

SEED = [
    {
        "nome": "João Silva",
        "conta": {"numero": "00001-1", "agencia": "0001", "balanco": 0.0, "limite": 500.0},
        "cartao": {"icone": ICONE_CREDITO, "descricao": "Cartão de crédito principal"},
        "news": [
            {"icone": ICONE_CREDITO, "descricao": "João Silva, invista hoje para garantir um futuro seguro e próspero. Seu futuro agradece!"}
        ],
    },
    {
        "nome": "Maria Oliveira",
        "conta": {"numero": "00002-2", "agencia": "0001", "balanco": 0.0, "limite": 500.0},
        "cartao": {"icone": ICONE_CREDITO, "descricao": "Cartão de crédito principal"},
        # bug corrigido: URL antiga estava sem "github." e quebrava o ícone
        "news": [
            {"icone": ICONE_CREDITO, "descricao": "Invista hoje para um futuro seguro e estável, Maria Oliveira. O seu futuro financeiro depende disso!"}
        ],
    },
    {
        "nome": "Antony Guimarães",
        "conta": {"numero": "00003-3", "agencia": "0001", "balanco": 0.0, "limite": 500.0},
        "cartao": {"icone": ICONE_CREDITO, "descricao": "Cartão de crédito principal"},
        "news": [
            {"icone": ICONE_CREDITO, "descricao": "Oi Tony, investir é a chave para multiplicar seu dinheiro. Não deixe sua grana parada!"}
        ],
    },
]


def seed_if_empty(session: Session) -> None:
    """Popula o banco com dados de exemplo apenas se ele estiver vazio."""
    ja_existe = session.exec(select(Usuario)).first()
    if ja_existe:
        return

    for item in SEED:
        usuario = Usuario(
            nome=item["nome"],
            conta=Conta(**item["conta"]),
            cartao=Cartao(**item["cartao"]),
            news=[News(**n) for n in item["news"]],
        )
        session.add(usuario)
    session.commit()


def seed_admin_if_empty(session: Session) -> None:
    """Cria o usuário administrador padrão (login da API) se ainda não existir.

    Credenciais vêm de variável de ambiente (ADMIN_USERNAME/ADMIN_PASSWORD);
    os defaults ('admin' / 'admin123') servem só para rodar localmente —
    troque em qualquer ambiente que não seja a sua própria máquina.
    """
    ja_existe = session.exec(select(AuthUser)).first()
    if ja_existe:
        return

    admin = AuthUser(
        username=settings.ADMIN_USERNAME,
        hashed_password=hash_password(settings.ADMIN_PASSWORD),
    )
    session.add(admin)
    session.commit()
