from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..core.auth import exigir_vendedor
from ..core.database import get_db
from ..services import reservas as service

router = APIRouter(prefix="/reservas", tags=["reservas"], dependencies=[Depends(exigir_vendedor)])


@router.get("", response_model=list[schemas.Reserva])
def listar_reservas(status: Literal["aguardando", "disponivel", "atendida", "cancelada"] | None = None, produto_id: int | None = None, db: Session = Depends(get_db)):
  """`status=disponivel` é quem já pode ser avisado para vir buscar."""
  return service.listar(db, status, produto_id)


@router.post("", response_model=schemas.Reserva, status_code=201)
def reservar(dados: schemas.ReservaCriar, db: Session = Depends(get_db)):
  """Só para título zerado (sem cópia na prateleira agora)."""
  return service.criar(db, dados)


@router.post("/{reserva_id}/atender", response_model=schemas.Aluguel)
def atender_reserva(reserva_id: int, dados: schemas.AtenderReserva, db: Session = Depends(get_db)):
  """Cliente veio buscar: abre o aluguel e fecha a reserva."""
  return service.atender(db, reserva_id, dados)


@router.delete("/{reserva_id}", status_code=204)
def cancelar_reserva(reserva_id: int, db: Session = Depends(get_db)):
  service.cancelar(db, reserva_id)
