from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, regras, schemas
from ..core.config import settings
from . import alugueis as alugueis_service


def serializar(db: Session, cliente: models.Cliente) -> schemas.Cliente:
    saida = schemas.Cliente.model_validate(cliente)
    plano = regras.plano_vigente(cliente)
    saida.plano_status = regras.status_do_plano(cliente)
    saida.bloqueado = regras.cliente_bloqueado(db, cliente.id)
    saida.locacoes_no_mes = regras.locacoes_no_mes(db, cliente.id)
    saida.limite_mensal = plano.limite_mensal if plano else None
    saida.limite_atingido = regras.limite_atingido(db, cliente)
    return saida


def listar(db: Session) -> list[schemas.Cliente]:
    clientes = db.query(models.Cliente).order_by(models.Cliente.nome).all()
    return [serializar(db, c) for c in clientes]


def obter(db: Session, cliente_id: int) -> models.Cliente:
    cliente = db.get(models.Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    return cliente


def _validar_plano(db: Session, plano_id: int | None) -> None:
    if plano_id and not db.get(models.Plano, plano_id):
        raise HTTPException(400, "Plano informado não existe.")


def _nova_mensalidade() -> date:
    return date.today() + timedelta(days=settings.DIAS_PLANO)


def criar(db: Session, dados: schemas.ClienteCriar) -> schemas.Cliente:
    _validar_plano(db, dados.plano_id)
    cliente = models.Cliente(**dados.model_dump())
    if cliente.plano_id:
        cliente.plano_vencimento = _nova_mensalidade()  # assinou hoje: primeira mensalidade
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return serializar(db, cliente)


def atualizar(db: Session, cliente_id: int, dados: schemas.ClienteAtualizar) -> schemas.Cliente:
    cliente = obter(db, cliente_id)
    valores = dados.model_dump(exclude_unset=True)
    if "plano_id" in valores:
        _validar_plano(db, valores["plano_id"])
        if valores["plano_id"] != cliente.plano_id:  # trocou, assinou ou cancelou o plano
            cliente.plano_vencimento = _nova_mensalidade() if valores["plano_id"] else None
    for campo, valor in valores.items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return serializar(db, cliente)


def excluir(db: Session, cliente_id: int) -> None:
    cliente = obter(db, cliente_id)
    em_aberto = (
        db.query(models.Aluguel)
        .filter(models.Aluguel.cliente_id == cliente_id, models.Aluguel.status != "devolvido")
        .first()
    )
    if em_aberto:
        raise HTTPException(409, "Cliente tem fita em aberto. Receba a devolução antes de excluir.")
    tem_historico = (
        db.query(models.Aluguel).filter(models.Aluguel.cliente_id == cliente_id).first()
        or db.query(models.Venda).filter(models.Venda.cliente_id == cliente_id).first()
    )
    if tem_historico:
        raise HTTPException(
            409, "Esse cliente tem aluguéis/vendas no histórico e não pode ser excluído."
        )
    db.delete(cliente)
    db.commit()


def renovar_plano(db: Session, cliente_id: int) -> schemas.RenovacaoPlano:
    """Cobra a próxima mensalidade. Se ainda está em dia, soma a partir do vencimento."""
    cliente = obter(db, cliente_id)
    if not cliente.plano:
        raise HTTPException(409, "Cliente não tem plano para renovar.")
    anterior = cliente.plano_vencimento
    base = max(date.today(), anterior) if anterior else date.today()
    cliente.plano_vencimento = base + timedelta(days=settings.DIAS_PLANO)
    db.commit()
    return schemas.RenovacaoPlano(
        cliente_id=cliente.id,
        plano=cliente.plano.nome,
        valor_cobrado=cliente.plano.preco_mensal,
        vencimento_anterior=anterior,
        novo_vencimento=cliente.plano_vencimento,
    )


def historico(db: Session, cliente_id: int) -> schemas.HistoricoCliente:
    cliente = obter(db, cliente_id)
    alugueis = sorted(cliente.alugueis, key=lambda a: (a.data_retirada, a.id), reverse=True)
    vendas = sorted(cliente.vendas, key=lambda v: (v.data, v.id), reverse=True)
    return schemas.HistoricoCliente(
        cliente=serializar(db, cliente),
        alugueis=[alugueis_service.serializar(a) for a in alugueis],
        vendas=[schemas.Venda.model_validate(v) for v in vendas],
    )
