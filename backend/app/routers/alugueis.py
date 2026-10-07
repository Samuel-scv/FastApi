from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..core.database import get_db
from ..services import alugueis as service

router = APIRouter(prefix="/alugueis", tags=["alugueis"])


@router.get("", response_model=list[schemas.Aluguel])
def listar_alugueis(
    status: Literal["ativo", "devolvido", "atrasado"] | None = None,
    db: Session = Depends(get_db),
):
    return service.listar(db, status)


@router.get("/{aluguel_id}", response_model=schemas.Aluguel)
def obter_aluguel(aluguel_id: int, db: Session = Depends(get_db)):
    return service.serializar(service.obter(db, aluguel_id))


@router.post("", response_model=schemas.Aluguel, status_code=201)
def registrar_aluguel(dados: schemas.AluguelCriar, db: Session = Depends(get_db)):
    return service.registrar(db, dados)


@router.post("/lote", response_model=list[schemas.Aluguel], status_code=201)
def registrar_aluguel_em_lote(dados: schemas.AluguelLoteCriar, db: Session = Depends(get_db)):
    return service.registrar_lote(db, dados)


@router.post("/{aluguel_id}/devolucao", response_model=schemas.Aluguel)
def devolver_aluguel(aluguel_id: int, dados: schemas.Devolucao, db: Session = Depends(get_db)):
    return service.devolver(db, aluguel_id, dados)
