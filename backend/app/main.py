from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine, SessionLocal
from .routers import produtos, clientes, planos, alugueis, vendas
from .dados_iniciais import popular_se_vazio

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Video Locadora Galaxia — API",
    description=(
        "API da videolocadora: acervo de produtos, clientes, planos de assinatura, "
        "aluguéis (com prazo e multa por atraso) e vendas definitivas."
    ),
    version="1.0.0",
)

# Libera o front (arquivo HTML local, GitHub Pages, etc.) a consumir a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(produtos.router)
app.include_router(clientes.router)
app.include_router(planos.router)
app.include_router(alugueis.router)
app.include_router(vendas.router)


@app.on_event("startup")
def preparar_dados_demo():
    db = SessionLocal()
    try:
        popular_se_vazio(db)
    finally:
        db.close()


@app.get("/", tags=["status"])
def raiz():
    return {"status": "no ar", "loja": "Video Locadora Galaxia", "docs": "/docs"}
