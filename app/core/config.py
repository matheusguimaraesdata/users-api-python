import os


class Settings:
    """Configurações da aplicação, lidas de variáveis de ambiente.

    Mantemos um default local em SQLite para não exigir infra extra,
    mas em produção (Railway) basta setar DATABASE_URL para Postgres.
    """

    PROJECT_NAME: str = "Users API — FastAPI + SQLModel"
    VERSION: str = "2.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")


settings = Settings()
