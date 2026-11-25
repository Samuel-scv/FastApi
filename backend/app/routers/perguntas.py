from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.auth import exigir_vendedor, usuario_atual
from ..core.database import get_db
from ..services import perguntas as service

router = APIRouter(prefix="/perguntas", tags=["perguntas"])


@router.get("/produto/{produto_id}", response_model=list[schemas.Pergunta])
def perguntas_do_titulo(produto_id: int, db: Session = Depends(get_db)):
  """Pública: perguntas já respondidas sobre o título (para a vitrine)."""
  return service.listar_publicas(db, produto_id)


@router.post("/produto/{produto_id}", response_model=schemas.Pergunta, status_code=201)
def perguntar(produto_id: int, dados: schemas.PerguntaCriar, usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  """Cliente logado pergunta sobre um filme ou série. Fica pendente até um vendedor responder."""
  return service.criar(db, produto_id, dados, usuario)


@router.get("/minhas", response_model=list[schemas.Pergunta])
def minhas_perguntas(usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  return service.listar_minhas(db, usuario)


@router.get("", response_model=list[schemas.Pergunta], dependencies=[Depends(exigir_vendedor)])
def caixa_de_entrada(status: Literal["pendente", "respondida"] | None = None, produto_id: int | None = None, db: Session = Depends(get_db)):
  """Vendedor: todas as perguntas. `status=pendente` é a fila para responder."""
  return service.listar_caixa(db, status, produto_id)


@router.post("/{pergunta_id}/resposta", response_model=schemas.Pergunta)
def responder(pergunta_id: int, dados: schemas.RespostaCriar, vendedor: models.Usuario = Depends(exigir_vendedor), db: Session = Depends(get_db)):
  return service.responder(db, pergunta_id, dados, vendedor)


@router.delete("/{pergunta_id}", status_code=204)
def excluir_pergunta(pergunta_id: int, usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  service.excluir(db, pergunta_id, usuario)
