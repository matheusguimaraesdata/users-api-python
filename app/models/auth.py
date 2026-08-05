from typing import Optional

from sqlmodel import Field, SQLModel


class AuthUser(SQLModel, table=True):
    """Usuário de autenticação (login da API) — não confundir com `Usuario`,
    que é a entidade de negócio (cliente do banco) gerenciada pelo CRUD."""

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"
