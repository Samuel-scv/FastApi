from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas

LIMITE_PENDENTES = 5  # por cliente, para barrar spam


def _primeiro_nome(nome: str) -> str:
  return nome.split()[0] if nome and nome.strip() else ""


def serializar(p: models.Pergunta) -> schemas.Pergunta:
  return schemas.Pergunta(id=p.id, produto_id=p.produto_id, titulo=p.produto.titulo, autor=_primeiro_nome(p.autor.nome), texto=p.texto, criada_em=p.criada_em, status="respondida" if p.resposta else "pendente", resposta=p.resposta, respondida_em=p.respondida_em, vendedor=_primeiro_nome(p.vendedor.nome) if p.vendedor else None)


def _obter(db: Session, pergunta_id: int) -> models.Pergunta:
  pergunta = db.get(models.Pergunta, pergunta_id)
  if not pergunta:
    raise HTTPException(404, "Pergunta não encontrada.")
  return pergunta


def _produto(db: Session, produto_id: int) -> models.Produto:
  produto = db.get(models.Produto, produto_id)
  if not produto:
    raise HTTPException(404, "Título não encontrado no acervo.")
  return produto


def criar(db: Session, produto_id: int, dados: schemas.PerguntaCriar, usuario: models.Usuario) -> schemas.Pergunta:
  produto = _produto(db, produto_id)
  pendentes = db.query(models.Pergunta).filter(models.Pergunta.autor_id == usuario.id, models.Pergunta.resposta.is_(None)).count()
  if pendentes >= LIMITE_PENDENTES:
    raise HTTPException(409, f"Você já tem {pendentes} perguntas aguardando resposta. Espere um vendedor responder.")
  pergunta = models.Pergunta(produto_id=produto.id, autor_id=usuario.id, texto=dados.texto)
  db.add(pergunta)
  db.commit()
  db.refresh(pergunta)
  return serializar(pergunta)


def listar_publicas(db: Session, produto_id: int) -> list[schemas.Pergunta]:
  """Vitrine do título: só as respondidas."""
  _produto(db, produto_id)
  perguntas = db.query(models.Pergunta).filter(models.Pergunta.produto_id == produto_id, models.Pergunta.resposta.isnot(None)).order_by(models.Pergunta.respondida_em.desc()).all()
  return [serializar(p) for p in perguntas]


def listar_minhas(db: Session, usuario: models.Usuario) -> list[schemas.Pergunta]:
  perguntas = db.query(models.Pergunta).filter(models.Pergunta.autor_id == usuario.id).order_by(models.Pergunta.id.desc()).all()
  return [serializar(p) for p in perguntas]


def listar_caixa(db: Session, status: str | None, produto_id: int | None) -> list[schemas.Pergunta]:
  """Caixa de entrada do vendedor. As pendentes saem na ordem de chegada (a mais antiga primeiro)."""
  query = db.query(models.Pergunta)
  if produto_id is not None:
    query = query.filter(models.Pergunta.produto_id == produto_id)
  if status == "pendente":
    query = query.filter(models.Pergunta.resposta.is_(None)).order_by(models.Pergunta.id)
  elif status == "respondida":
    query = query.filter(models.Pergunta.resposta.isnot(None)).order_by(models.Pergunta.respondida_em.desc())
  else:
    query = query.order_by(models.Pergunta.id.desc())
  return [serializar(p) for p in query.all()]


def responder(db: Session, pergunta_id: int, dados: schemas.RespostaCriar, vendedor: models.Usuario) -> schemas.Pergunta:
  pergunta = _obter(db, pergunta_id)
  if pergunta.resposta:
    raise HTTPException(409, "Essa pergunta já foi respondida.")
  pergunta.resposta = dados.texto
  pergunta.respondida_em = datetime.now(timezone.utc)
  pergunta.vendedor_id = vendedor.id
  db.commit()
  db.refresh(pergunta)
  return serializar(pergunta)


def excluir(db: Session, pergunta_id: int, usuario: models.Usuario) -> None:
  """Vendedor/admin apaga qualquer uma (moderação). O autor só apaga a sua enquanto ninguém respondeu."""
  pergunta = _obter(db, pergunta_id)
  equipe = usuario.vendedor or usuario.admin
  if not equipe and not (pergunta.autor_id == usuario.id and not pergunta.resposta):
    raise HTTPException(403, "Você só pode apagar a sua própria pergunta enquanto ela não foi respondida.")
  db.delete(pergunta)
  db.commit()
