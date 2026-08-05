import os


class Settings:
    """Configurações da aplicação, lidas de variáveis de ambiente.

    Mantemos um default local em SQLite para não exigir infra extra,
    mas em produção (Railway) basta setar DATABASE_URL para Postgres.
    """

    PROJECT_NAME: str = "Users API — FastAPI + SQLModel"
    VERSION: str = "3.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")

    # --- Autenticação ---
    # Em produção, SECRET_KEY deve vir de variável de ambiente (nunca hardcoded).
    # O valor abaixo só existe pra rodar localmente sem configuração extra.
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-trocar-em-producao")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    # Usuário administrador criado automaticamente no primeiro boot (só para demo/portfólio).
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")


settings = Settings()

