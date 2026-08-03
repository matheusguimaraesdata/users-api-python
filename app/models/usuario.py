from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# ---------------------------------------------------------------------------
# TABELAS (persistidas no banco)
# ---------------------------------------------------------------------------

class Conta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    numero: str
    agencia: str
    balanco: float = 0.0
    limite: float = 0.0

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional["Usuario"] = Relationship(back_populates="conta")


class Cartao(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    icone: str
    descricao: str

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional["Usuario"] = Relationship(back_populates="cartao")


class Recurso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    icone: str
    descricao: str

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional["Usuario"] = Relationship(back_populates="recurso")


class News(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    icone: str
    descricao: str

    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")
    usuario: Optional["Usuario"] = Relationship(back_populates="news")


class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str

    conta: Optional[Conta] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )
    cartao: Optional[Cartao] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )
    recurso: List[Recurso] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    news: List[News] = Relationship(
        back_populates="usuario",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# ---------------------------------------------------------------------------
# SCHEMAS (entrada/saída da API — não são tabelas)
# ---------------------------------------------------------------------------

class ContaSchema(SQLModel):
    id: Optional[int] = None
    numero: str
    agencia: str
    balanco: float = 0.0
    limite: float = 0.0


class CartaoSchema(SQLModel):
    id: Optional[int] = None
    icone: str
    descricao: str


class RecursoSchema(SQLModel):
    id: Optional[int] = None
    icone: str
    descricao: str


class NewsSchema(SQLModel):
    id: Optional[int] = None
    icone: str
    descricao: str


class UsuarioCreate(SQLModel):
    nome: str
    conta: ContaSchema
    cartao: CartaoSchema
    recurso: List[RecursoSchema] = []
    news: List[NewsSchema] = []


class UsuarioUpdate(SQLModel):
    """Todos os campos opcionais — usado no PATCH (atualização parcial)."""
    nome: Optional[str] = None
    conta: Optional[ContaSchema] = None
    cartao: Optional[CartaoSchema] = None
    recurso: Optional[List[RecursoSchema]] = None
    news: Optional[List[NewsSchema]] = None


class UsuarioRead(SQLModel):
    id: int
    nome: str
    conta: Optional[ContaSchema] = None
    cartao: Optional[CartaoSchema] = None
    recurso: List[RecursoSchema] = []
    news: List[NewsSchema] = []
