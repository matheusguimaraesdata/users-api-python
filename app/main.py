from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from app.core.config import settings
from app.db.database import engine, init_db
from app.db.seed import seed_if_empty
from app.routers import relatorios, usuario


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda na inicialização: cria as tabelas e popula dados de exemplo se vazio."""
    init_db()
    with Session(engine) as session:
        seed_if_empty(session)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "API de usuários, contas, cartões, recursos e news, com persistência "
        "real em banco relacional e endpoints de analytics (Pandas) para "
        "consumo por pipelines de ETL e ferramentas de BI."
    ),
    version=settings.VERSION,
    lifespan=lifespan,
)

app.include_router(usuario.router)
app.include_router(relatorios.router)


@app.get("/", tags=["Status"])
def root():
    return {"status": "API online. Acesse /docs para o Swagger."}
