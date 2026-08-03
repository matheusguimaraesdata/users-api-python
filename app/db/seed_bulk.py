"""
Gerador de massa de dados sintética para a base de usuários.

Reaproveita a mesma modelagem de domínio (Usuario -> Conta, Cartao, Recurso,
News) usada no seed original, mas gera N registros realistas via Faker —
útil para: popular ambiente de demonstração, testar paginação/filtro,
e dar volume real para os endpoints de analytics (/relatorios/estatisticas).
"""
import random

from faker import Faker
from sqlmodel import Session

from app.models.usuario import Cartao, Conta, News, Recurso, Usuario

fake = Faker("pt_BR")

AGENCIAS = ["0001", "0002", "0003", "0004"]
DESCRICOES_CARTAO = [
    "Cartão de crédito principal",
    "Cartão adicional",
    "Cartão empresarial",
    "Cartão de débito",
]
ICONES = [
    "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/credit.svg",
    "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/wallet.svg",
    "https://digitalinnovationone.github.io/santander-dev-week-2023-api/icons/pig.svg",
]
DESCRICOES_RECURSO = [
    "Empréstimo pré-aprovado",
    "Seguro de vida em oferta",
    "Cashback em compras",
    "Programa de pontos",
    "Investimento automático",
]


def _gerar_usuario() -> Usuario:
    nome = fake.name()
    numero_conta = f"{fake.unique.random_number(digits=5, fix_len=True)}-{random.randint(0, 9)}"
    limite = round(random.uniform(300.0, 15000.0), 2)
    balanco = round(random.uniform(-500.0, limite), 2)

    conta = Conta(
        numero=numero_conta,
        agencia=random.choice(AGENCIAS),
        balanco=balanco,
        limite=limite,
    )
    cartao = Cartao(
        icone=random.choice(ICONES),
        descricao=random.choice(DESCRICOES_CARTAO),
    )
    recursos = [
        Recurso(icone=random.choice(ICONES), descricao=desc)
        for desc in random.sample(DESCRICOES_RECURSO, k=random.randint(0, 3))
    ]
    news = [
        News(icone=random.choice(ICONES), descricao=f"{nome.split()[0]}, {fake.sentence(nb_words=10)}")
        for _ in range(random.randint(0, 2))
    ]

    return Usuario(nome=nome, conta=conta, cartao=cartao, recurso=recursos, news=news)


def seed_bulk(session: Session, quantidade: int = 100, seed: int | None = 42) -> int:
    """Insere `quantidade` usuários sintéticos no banco. Retorna quantos foram criados."""
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)
    fake.unique.clear()

    usuarios = [_gerar_usuario() for _ in range(quantidade)]
    session.add_all(usuarios)
    session.commit()
    return len(usuarios)
