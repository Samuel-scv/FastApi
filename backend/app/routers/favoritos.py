from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.auth import usuario_atual
from ..core.database import get_db
from ..services import favoritos as service

router = APIRouter(prefix="/favoritos", tags=["favoritos"], dependencies=[Depends(usuario_atual)])


@router.get("", response_model=list[schemas.Favorito])
def meus_favoritos(usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  return service.listar(db, usuario.id)


@router.post("/{produto_id}", response_model=schemas.Favorito, status_code=201)
def adicionar_favorito(produto_id: int, usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  return service.adicionar(db, usuario.id, produto_id)


@router.delete("/{produto_id}", status_code=204)
def remover_favorito(produto_id: int, usuario: models.Usuario = Depends(usuario_atual), db: Session = Depends(get_db)):
  service.remover(db, usuario.id, produto_id)
