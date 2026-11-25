from sqlalchemy import func
from sqlalchemy.orm import Session

from fastapi import HTTPException

from .. import models, schemas
from ..core.paginacao import montar, paginar


def _primeiro_nome(nome: str) -> str:
  return nome.split()[0] if nome and nome.strip() else ""


def _serializar(a: models.Avaliacao) -> schemas.Avaliacao:
  return schemas.Avaliacao(id=a.id, produto_id=a.produto_id, cliente=_primeiro_nome(a.cliente.nome), nota=a.nota, comentario=a.comentario, criada_em=a.criada_em)


def media_do_produto(db: Session, produto_id: int) -> tuple[float | None, int]:
  media, total = db.query(func.avg(models.Avaliacao.nota), func.count(models.Avaliacao.id)).filter(models.Avaliacao.produto_id == produto_id).one()
  return (round(media, 1) if media is not None else None, total)


def _cliente_do_usuario(db: Session, usuario_id: int) -> models.Cliente:
  cliente = db.query(models.Cliente).filter(models.Cliente.usuario_id == usuario_id).first()
  if not cliente:
    raise HTTPException(409, "Sua conta ainda não está vinculada a um cadastro de cliente. Peça para o balcão vincular.")
  return cliente


def criar(db: Session, produto_id: int, dados: schemas.AvaliacaoCriar, usuario: models.Usuario) -> schemas.Avaliacao:
  if not db.get(models.Produto, produto_id):
    raise HTTPException(404, "Título não encontrado no acervo.")
  cliente = _cliente_do_usuario(db, usuario.id)
  ja_levou = (
    db.query(models.Aluguel).filter(models.Aluguel.cliente_id == cliente.id, models.Aluguel.produto_id == produto_id).first()
    or db.query(models.Venda).filter(models.Venda.cliente_id == cliente.id, models.Venda.produto_id == produto_id).first()
  )
  if not ja_levou:
    raise HTTPException(403, "Você só pode avaliar títulos que já alugou ou comprou.")
  if db.query(models.Avaliacao).filter(models.Avaliacao.produto_id == produto_id, models.Avaliacao.cliente_id == cliente.id).first():
    raise HTTPException(409, "Você já avaliou esse título.")
  avaliacao = models.Avaliacao(produto_id=produto_id, cliente_id=cliente.id, nota=dados.nota, comentario=dados.comentario)
  db.add(avaliacao)
  db.commit()
  db.refresh(avaliacao)
  return _serializar(avaliacao)


def listar_do_produto(db: Session, produto_id: int, pagina: int = 1, por_pagina: int = 20) -> dict:
  query = db.query(models.Avaliacao).filter(models.Avaliacao.produto_id == produto_id).order_by(models.Avaliacao.id.desc())
  avaliacoes, total = paginar(query, pagina, por_pagina)
  return montar([_serializar(a) for a in avaliacoes], total, pagina, por_pagina)
