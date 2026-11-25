from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.auth import usuario_atual
from ..core.database import get_db
from ..core.paginacao import Pagina
from ..services import avaliacoes as service

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


@router.get("/produto/{produto_id}", response_model=Pagina[schemas.Avaliacao])
def avaliacoes_do_titulo(produto_id: int, pagina: int = 1, por_pagina: int = 20, db: Session = Depends(get_db)):
  """Pública: avaliações do título, para a vitrine."""
  return service.listar_do_produto(db, produto_id, pagina, por_pagina)


@router.post("/produto/{produto_id}", response_model=schemas.Avaliacao, status_code=201)
def avaliar(produto_id: int, dados: schemas.AvaliacaoCriar, usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  """Cliente logado avalia um título que já alugou ou comprou. Uma avaliação por título."""
  return service.criar(db, produto_id, dados, usuario)
