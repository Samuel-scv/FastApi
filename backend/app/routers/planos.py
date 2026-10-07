from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..core.database import get_db
from ..services import planos as service

router = APIRouter(prefix="/planos", tags=["planos"])


@router.get("", response_model=list[schemas.Plano])
def listar_planos(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get("/{plano_id}", response_model=schemas.Plano)
def obter_plano(plano_id: int, db: Session = Depends(get_db)):
    return service.obter(db, plano_id)


@router.post("", response_model=schemas.Plano, status_code=201)
def criar_plano(dados: schemas.PlanoCriar, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.put("/{plano_id}", response_model=schemas.Plano)
def atualizar_plano(plano_id: int, dados: schemas.PlanoAtualizar, db: Session = Depends(get_db)):
    return service.atualizar(db, plano_id, dados)


@router.delete("/{plano_id}", status_code=204)
def excluir_plano(plano_id: int, db: Session = Depends(get_db)):
    service.excluir(db, plano_id)
