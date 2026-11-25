from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas


def listar(db: Session, usuario_id: int) -> list[schemas.Favorito]:
  favoritos = db.query(models.Favorito).filter(models.Favorito.usuario_id == usuario_id).order_by(models.Favorito.id.desc()).all()
  return [schemas.Favorito(id=f.id, produto_id=f.produto_id, titulo=f.produto.titulo, criado_em=f.criado_em) for f in favoritos]


def adicionar(db: Session, usuario_id: int, produto_id: int) -> schemas.Favorito:
  if not db.get(models.Produto, produto_id):
    raise HTTPException(404, "Título não encontrado no acervo.")
  existente = db.query(models.Favorito).filter(models.Favorito.usuario_id == usuario_id, models.Favorito.produto_id == produto_id).first()
  if existente:
    raise HTTPException(409, "Esse título já está nos seus favoritos.")
  favorito = models.Favorito(usuario_id=usuario_id, produto_id=produto_id)
  db.add(favorito)
  db.commit()
  db.refresh(favorito)
  return schemas.Favorito(id=favorito.id, produto_id=favorito.produto_id, titulo=favorito.produto.titulo, criado_em=favorito.criado_em)


def remover(db: Session, usuario_id: int, produto_id: int) -> None:
  favorito = db.query(models.Favorito).filter(models.Favorito.usuario_id == usuario_id, models.Favorito.produto_id == produto_id).first()
  if not favorito:
    raise HTTPException(404, "Esse título não está nos seus favoritos.")
  db.delete(favorito)
  db.commit()
