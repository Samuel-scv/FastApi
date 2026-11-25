from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..core.auth import exigir_admin
from ..core.paginacao import Pagina
from ..core.database import get_db
from ..services import produtos as service

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("", response_model=Pagina[schemas.Produto])
def listar_produtos(
    pagina: int = Query(1, ge=1),
    por_pagina: int = Query(20, ge=1, le=100),
    q: str | None = None,
    genero: str | None = None,
    diretor: str | None = None,
    tipo: Literal["filme", "serie"] | None = None,
    disponivel: bool | None = None,
    ordenar_por: Literal["titulo", "nota", "ano", "preco_aluguel"] = "titulo",
    db: Session = Depends(get_db),
):
    """`q` busca por texto no título. `ordenar_por=nota` mostra os mais bem avaliados primeiro."""
    return service.listar(db, pagina, por_pagina, q, genero, diretor, tipo, disponivel, ordenar_por)


@router.get("/{produto_id}", response_model=schemas.Produto)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    return service.obter_com_avaliacao(db, produto_id)


@router.post("", response_model=schemas.Produto, status_code=201, dependencies=[Depends(exigir_admin)])
def criar_produto(dados: schemas.ProdutoCriar, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.put("/{produto_id}", response_model=schemas.Produto, dependencies=[Depends(exigir_admin)])
def atualizar_produto(produto_id: int, dados: schemas.ProdutoAtualizar, db: Session = Depends(get_db)):
    return service.atualizar(db, produto_id, dados)


@router.delete("/{produto_id}", status_code=204, dependencies=[Depends(exigir_admin)])
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    service.excluir(db, produto_id)
