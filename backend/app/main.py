from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (registra as tabelas no Base)
from .core.config import settings
from .core.database import Base, SessionLocal, atualizar_esquema_sqlite, engine
from .routers import alugueis, clientes, planos, produtos, vendas
from .seeds.dados_iniciais import popular_se_vazio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: cria as tabelas e carrega os dados de exemplo no primeiro uso.
    Base.metadata.create_all(bind=engine)
    atualizar_esquema_sqlite()
    db = SessionLocal()
    try:
        popular_se_vazio(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Video Locadora Galaxia — API",
    description=(
        "API da videolocadora: acervo de produtos, clientes, planos de assinatura, "
        "aluguéis (com prazo e multa por atraso) e vendas definitivas."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

# Libera o front (arquivo HTML local, GitHub Pages, etc.) a consumir a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(clientes.router)
app.include_router(planos.router)
app.include_router(alugueis.router)
app.include_router(vendas.router)


@app.get("/", tags=["status"])
def raiz():
    return {"status": "no ar", "loja": "Video Locadora Galaxia", "docs": "/docs"}


@app.get("/health", tags=["status"])
def health():
    """Usado pelo healthcheck do Docker."""
    return {"status": "ok"}