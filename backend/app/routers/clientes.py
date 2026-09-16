from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas, regras
from ..database import get_db

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _serializar(db: Session, cliente: models.Cliente) -> schemas.Cliente:
    saida = schemas.Cliente.model_validate(cliente)
    saida.bloqueado = regras.cliente_bloqueado(db, cliente.id)
    saida.locacoes_no_mes = regras.locacoes_no_mes(db, cliente.id)
    return saida


@router.get("", response_model=list[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).order_by(models.Cliente.nome).all()
    return [_serializar(db, c) for c in clientes]


@router.get("/{cliente_id}", response_model=schemas.Cliente)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(models.Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    return _serializar(db, cliente)


@router.post("", response_model=schemas.Cliente, status_code=201)
def criar_cliente(dados: schemas.ClienteCriar, db: Session = Depends(get_db)):
    if dados.plano_id and not db.get(models.Plano, dados.plano_id):
        raise HTTPException(400, "Plano informado não existe.")
    cliente = models.Cliente(**dados.model_dump())
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return _serializar(db, cliente)


@router.put("/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, dados: schemas.ClienteAtualizar, db: Session = Depends(get_db)):
    cliente = db.get(models.Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    valores = dados.model_dump(exclude_unset=True)
    if valores.get("plano_id") and not db.get(models.Plano, valores["plano_id"]):
        raise HTTPException(400, "Plano informado não existe.")
    for campo, valor in valores.items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return _serializar(db, cliente)


@router.delete("/{cliente_id}", status_code=204)
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.get(models.Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    em_aberto = (
        db.query(models.Aluguel)
        .filter(models.Aluguel.cliente_id == cliente_id, models.Aluguel.status != "devolvido")
        .first()
    )
    if em_aberto:
        raise HTTPException(409, "Cliente tem fita em aberto. Receba a devolução antes de excluir.")
    db.delete(cliente)
    db.commit()
