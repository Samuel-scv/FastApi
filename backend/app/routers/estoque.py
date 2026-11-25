from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.auth import exigir_admin, exigir_vendedor
from ..core.paginacao import Pagina
from ..core.database import get_db
from ..services import estoque as service

router = APIRouter(prefix="/estoque", tags=["estoque"], dependencies=[Depends(exigir_vendedor)])


@router.get("", response_model=schemas.ResumoEstoque)
def resumo_do_estoque(tipo: Literal["filme", "serie"] | None = None, situacao: Literal["ok", "baixo", "zerado"] | None = None, db: Session = Depends(get_db)):
  """Posição do estoque por título. `situacao=baixo` lista o que precisa ser reposto."""
  return service.resumo(db, tipo, situacao)


@router.get("/movimentos", response_model=Pagina[schemas.MovimentoEstoque])
def listar_movimentos(produto_id: int | None = None, tipo: schemas.estoque.TipoMovimento | None = None, pagina: int = 1, por_pagina: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
  return service.listar_movimentos(db, produto_id, tipo, pagina, por_pagina)


@router.post("/{produto_id}/entrada", response_model=schemas.MovimentoEstoque, status_code=201)
def dar_entrada(produto_id: int, dados: schemas.EntradaEstoque, usuario: models.Usuario = Depends(exigir_vendedor), db: Session = Depends(get_db)):
  """Chegada de cópias novas (compra, doação)."""
  return service.entrada(db, produto_id, dados, usuario.id)


@router.post("/{produto_id}/perda", response_model=schemas.MovimentoEstoque, status_code=201)
def dar_baixa_por_perda(produto_id: int, dados: schemas.PerdaEstoque, usuario: models.Usuario = Depends(exigir_admin), db: Session = Depends(get_db)):
  """Baixa de cópia danificada ou extraviada. Só admin."""
  return service.perda(db, produto_id, dados, usuario.id)


@router.post("/{produto_id}/ajuste", response_model=schemas.MovimentoEstoque, status_code=201)
def ajustar_estoque(produto_id: int, dados: schemas.AjusteEstoque, usuario: models.Usuario = Depends(exigir_admin), db: Session = Depends(get_db)):
  """Inventário: informa a contagem real e o sistema registra a diferença. Só admin."""
  return service.ajustar(db, produto_id, dados, usuario.id)
