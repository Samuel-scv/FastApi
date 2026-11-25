from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from . import alugueis as alugueis_service


def _serializar(r: models.Reserva, posicao: int | None = None) -> schemas.Reserva:
  return schemas.Reserva(
    id=r.id, produto_id=r.produto_id, titulo=r.produto.titulo, cliente_id=r.cliente_id, cliente=r.cliente.nome,
    posicao_na_fila=posicao, status=r.status, criada_em=r.criada_em, disponivel_em=r.disponivel_em,
  )


def _fila_aguardando(db: Session, produto_id: int) -> list[models.Reserva]:
  return db.query(models.Reserva).filter(models.Reserva.produto_id == produto_id, models.Reserva.status == "aguardando").order_by(models.Reserva.criada_em).all()


def promover_fila(db: Session, produto: models.Produto) -> None:
  """Chamada sempre que o estoque de um título aumenta (entrada ou devolução).

  Marca como "disponivel" (chegou a vez) quem está há mais tempo esperando, até o limite
  de cópias livres. A cópia continua fisicamente na prateleira até o balcão confirmar a
  retirada em `/reservas/{id}/atender` — então um vendedor ainda pode alugá-la direto para
  outra pessoa nesse meio-tempo; é uma simplificação aceitável para o tamanho do projeto.
  """
  ja_reservadas = db.query(models.Reserva).filter(models.Reserva.produto_id == produto.id, models.Reserva.status == "disponivel").count()
  livres = produto.estoque - ja_reservadas
  if livres <= 0:
    return
  from datetime import datetime, timezone

  for reserva in _fila_aguardando(db, produto.id)[:livres]:
    reserva.status = "disponivel"
    reserva.disponivel_em = datetime.now(timezone.utc)


def criar(db: Session, dados: schemas.ReservaCriar) -> schemas.Reserva:
  produto = db.get(models.Produto, dados.produto_id)
  if not produto:
    raise HTTPException(404, "Título não encontrado no acervo.")
  if not db.get(models.Cliente, dados.cliente_id):
    raise HTTPException(404, "Cliente não encontrado.")
  if produto.estoque > 0:
    raise HTTPException(409, f"Há cópia de '{produto.titulo}' disponível agora; não precisa reservar.")
  existente = (
    db.query(models.Reserva)
    .filter(models.Reserva.produto_id == dados.produto_id, models.Reserva.cliente_id == dados.cliente_id, models.Reserva.status.in_(["aguardando", "disponivel"]))
    .first()
  )
  if existente:
    raise HTTPException(409, "Esse cliente já está na fila desse título.")
  reserva = models.Reserva(produto_id=dados.produto_id, cliente_id=dados.cliente_id)
  db.add(reserva)
  db.commit()
  db.refresh(reserva)
  posicao = len(_fila_aguardando(db, dados.produto_id))
  return _serializar(reserva, posicao)


def listar(db: Session, status: str | None = None, produto_id: int | None = None) -> list[schemas.Reserva]:
  query = db.query(models.Reserva)
  if produto_id is not None:
    query = query.filter(models.Reserva.produto_id == produto_id)
  if status:
    query = query.filter(models.Reserva.status == status)
  reservas = query.order_by(models.Reserva.criada_em).all()
  filas: dict[int, int] = {}
  saida = []
  for r in reservas:
    posicao = None
    if r.status == "aguardando":
      filas[r.produto_id] = filas.get(r.produto_id, 0) + 1
      posicao = filas[r.produto_id]
    saida.append(_serializar(r, posicao))
  return saida


def _obter(db: Session, reserva_id: int) -> models.Reserva:
  reserva = db.get(models.Reserva, reserva_id)
  if not reserva:
    raise HTTPException(404, "Reserva não encontrada.")
  return reserva


def cancelar(db: Session, reserva_id: int) -> None:
  reserva = _obter(db, reserva_id)
  if reserva.status in ("atendida", "cancelada"):
    raise HTTPException(409, f"Essa reserva já está {reserva.status}.")
  era_disponivel = reserva.status == "disponivel"
  reserva.status = "cancelada"
  db.commit()
  if era_disponivel:  # libera a vaga para o próximo da fila
    promover_fila(db, reserva.produto)
    db.commit()


def atender(db: Session, reserva_id: int, dados: schemas.AtenderReserva) -> schemas.Aluguel:
  """Confirma que o cliente veio buscar: vira um aluguel normal e fecha a reserva."""
  reserva = _obter(db, reserva_id)
  if reserva.status != "disponivel":
    raise HTTPException(409, "Essa reserva ainda não está disponível para retirada.")
  aluguel = alugueis_service.registrar(db, schemas.AluguelCriar(cliente_id=reserva.cliente_id, produto_id=reserva.produto_id, dias=dados.dias))
  reserva.status = "atendida"
  db.commit()
  return aluguel
