import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Users API — FastAPI + SQLModel"
    VERSION: str = "3.0.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./database.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave-de-desenvolvimento-trocar-em-producao")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    def __init__(self):
        is_production = not self.DATABASE_URL.startswith("sqlite")
        using_default_secret = self.SECRET_KEY == "chave-de-desenvolvimento-trocar-em-producao"
        using_default_admin_pw = self.ADMIN_PASSWORD == "admin123"

        if is_production and (using_default_secret or using_default_admin_pw):
            raise RuntimeError(
                "SECRET_KEY e ADMIN_PASSWORD precisam ser configurados via variável de "
                "ambiente quando DATABASE_URL aponta para produção (não-SQLite)."
            )


settings = Settings()