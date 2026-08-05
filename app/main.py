from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.core.config import settings
from app.db.database import engine, init_db
from app.db.seed import seed_admin_if_empty, seed_if_empty
from app.routers import auth, relatorios, usuario


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Roda na inicialização: cria as tabelas e popula dados de exemplo se vazio."""
    init_db()
    with Session(engine) as session:
        seed_if_empty(session)
        seed_admin_if_empty(session)
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
    docs_url=None,  # substituído abaixo por uma versão que não depende de CDN externa
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/docs", include_in_schema=False)
def docs():
    """Swagger UI servido com assets locais — funciona mesmo sem acesso à internet
    (útil atrás de firewall corporativo, já que o padrão do FastAPI depende de CDN)."""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} — Docs",
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="/static/swagger-ui/favicon-32x32.png",
    )


app.include_router(auth.router)
app.include_router(usuario.router)
app.include_router(relatorios.router)


@app.get("/", tags=["Status"])
def root():
    return {"status": "API online. Acesse /docs para o Swagger."}
