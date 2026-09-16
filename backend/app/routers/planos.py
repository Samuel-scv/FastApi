from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/planos", tags=["planos"])


@router.get("", response_model=list[schemas.Plano])
def listar_planos(db: Session = Depends(get_db)):
    return db.query(models.Plano).order_by(models.Plano.preco_mensal).all()


@router.get("/{plano_id}", response_model=schemas.Plano)
def obter_plano(plano_id: int, db: Session = Depends(get_db)):
    plano = db.get(models.Plano, plano_id)
    if not plano:
        raise HTTPException(404, "Plano não encontrado.")
    return plano


@router.post("", response_model=schemas.Plano, status_code=201)
def criar_plano(dados: schemas.PlanoCriar, db: Session = Depends(get_db)):
    plano = models.Plano(**dados.model_dump())
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return plano


@router.put("/{plano_id}", response_model=schemas.Plano)
def atualizar_plano(plano_id: int, dados: schemas.PlanoAtualizar, db: Session = Depends(get_db)):
    plano = db.get(models.Plano, plano_id)
    if not plano:
        raise HTTPException(404, "Plano não encontrado.")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(plano, campo, valor)
    db.commit()
    db.refresh(plano)
    return plano


@router.delete("/{plano_id}", status_code=204)
def excluir_plano(plano_id: int, db: Session = Depends(get_db)):
    plano = db.get(models.Plano, plano_id)
    if not plano:
        raise HTTPException(404, "Plano não encontrado.")
    assinante = db.query(models.Cliente).filter(models.Cliente.plano_id == plano_id).first()
    if assinante:
        raise HTTPException(409, "Há clientes assinando esse plano. Migre-os antes de excluir.")
    db.delete(plano)
    db.commit()
