from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas, regras
from ..database import get_db

router = APIRouter(prefix="/alugueis", tags=["alugueis"])


def _serializar(aluguel: models.Aluguel) -> schemas.Aluguel:
    saida = schemas.Aluguel.model_validate(aluguel)
    saida.dias_atraso = regras.dias_de_atraso(aluguel)
    saida.multa_estimada = regras.calcular_multa(aluguel)
    return saida


@router.get("", response_model=list[schemas.Aluguel])
def listar_alugueis(status: str | None = None, db: Session = Depends(get_db)):
    query = db.query(models.Aluguel).options(
        joinedload(models.Aluguel.cliente).joinedload(models.Cliente.plano)
    )
    if status:
        query = query.filter(models.Aluguel.status == status)
    alugueis = query.order_by(models.Aluguel.data_retirada.desc()).all()
    return [_serializar(a) for a in alugueis]


@router.get("/{aluguel_id}", response_model=schemas.Aluguel)
def obter_aluguel(aluguel_id: int, db: Session = Depends(get_db)):
    aluguel = db.get(models.Aluguel, aluguel_id)
    if not aluguel:
        raise HTTPException(404, "Aluguel não encontrado.")
    return _serializar(aluguel)


@router.post("", response_model=schemas.Aluguel, status_code=201)
def registrar_aluguel(dados: schemas.AluguelCriar, db: Session = Depends(get_db)):
    cliente = db.get(models.Cliente, dados.cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    produto = db.get(models.Produto, dados.produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")

    if regras.cliente_bloqueado(db, cliente.id):
        raise HTTPException(409, "Cliente bloqueado por devolução em atraso.")
    if produto.estoque < 1:
        raise HTTPException(409, "Não há cópia disponível desse título.")

    dias_bonus = cliente.plano.dias_bonus if cliente.plano else 0
    hoje = date.today()

    aluguel = models.Aluguel(
        cliente_id=cliente.id,
        produto_id=produto.id,
        data_retirada=hoje,
        data_prevista=hoje + timedelta(days=dados.dias + dias_bonus),
        valor=produto.preco_aluguel,
        multa_paga=0,
        status="ativo",
    )
    produto.estoque -= 1
    db.add(aluguel)
    db.commit()
    db.refresh(aluguel)
    return _serializar(aluguel)


@router.post("/{aluguel_id}/devolucao", response_model=schemas.Aluguel)
def devolver_aluguel(aluguel_id: int, dados: schemas.Devolucao, db: Session = Depends(get_db)):
    aluguel = db.get(models.Aluguel, aluguel_id)
    if not aluguel:
        raise HTTPException(404, "Aluguel não encontrado.")
    if aluguel.status == "devolvido":
        raise HTTPException(409, "Esse aluguel já foi devolvido.")

    aluguel.data_devolucao = dados.data_devolucao or date.today()
    aluguel.multa_paga = (
        dados.multa if dados.multa is not None else regras.calcular_multa(aluguel)
    )
    aluguel.status = "devolvido"

    produto = db.get(models.Produto, aluguel.produto_id)
    if produto:
        produto.estoque += 1

    db.commit()
    db.refresh(aluguel)
    return _serializar(aluguel)
