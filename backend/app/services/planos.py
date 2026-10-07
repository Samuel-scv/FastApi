from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas


def listar(db: Session) -> list[models.Plano]:
    return db.query(models.Plano).order_by(models.Plano.preco_mensal).all()


def obter(db: Session, plano_id: int) -> models.Plano:
    plano = db.get(models.Plano, plano_id)
    if not plano:
        raise HTTPException(404, "Plano não encontrado.")
    return plano


def criar(db: Session, dados: schemas.PlanoCriar) -> models.Plano:
    plano = models.Plano(**dados.model_dump())
    db.add(plano)
    db.commit()
    db.refresh(plano)
    return plano


def atualizar(db: Session, plano_id: int, dados: schemas.PlanoAtualizar) -> models.Plano:
    plano = obter(db, plano_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(plano, campo, valor)
    db.commit()
    db.refresh(plano)
    return plano


def excluir(db: Session, plano_id: int) -> None:
    plano = obter(db, plano_id)
    assinante = db.query(models.Cliente).filter(models.Cliente.plano_id == plano_id).first()
    if assinante:
        raise HTTPException(409, "Há clientes assinando esse plano. Migre-os antes de excluir.")
    db.delete(plano)
    db.commit()
