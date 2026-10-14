from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models, regras, schemas


def serializar(aluguel: models.Aluguel) -> schemas.Aluguel:
    saida = schemas.Aluguel.model_validate(aluguel)
    saida.dias_atraso = regras.dias_de_atraso(aluguel)
    saida.multa_estimada = regras.calcular_multa(aluguel)
    return saida


def listar(db: Session, status: str | None = None) -> list[schemas.Aluguel]:
    """status: ativo | devolvido | atrasado (ativo com prazo vencido)."""
    query = db.query(models.Aluguel).options(
        joinedload(models.Aluguel.cliente).joinedload(models.Cliente.plano)
    )
    if status in ("ativo", "devolvido"):
        query = query.filter(models.Aluguel.status == status)
    alugueis = query.order_by(models.Aluguel.data_retirada.desc(), models.Aluguel.id.desc()).all()
    if status == "atrasado":
        alugueis = [a for a in alugueis if regras.esta_atrasado(a)]
    return [serializar(a) for a in alugueis]


def obter(db: Session, aluguel_id: int) -> models.Aluguel:
    aluguel = db.get(models.Aluguel, aluguel_id)
    if not aluguel:
        raise HTTPException(404, "Aluguel não encontrado.")
    return aluguel


def _cliente_liberado(db: Session, cliente_id: int) -> models.Cliente:
    cliente = db.get(models.Cliente, cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    if regras.cliente_bloqueado(db, cliente.id):
        raise HTTPException(409, "Cliente bloqueado por devolução em atraso.")
    return cliente


def _titulo_disponivel(db: Session, produto_id: int) -> models.Produto:
    produto = db.get(models.Produto, produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    if produto.estoque < 1:
        raise HTTPException(409, f"Não há cópia disponível de '{produto.titulo}'.")
    return produto


def _abrir(db: Session, cliente: models.Cliente, produto: models.Produto, dias: int) -> models.Aluguel:
    hoje = date.today()
    plano = regras.plano_vigente(cliente, hoje)  # plano vencido não dá dias extras
    bonus = plano.dias_bonus if plano else 0
    aluguel = models.Aluguel(
        cliente_id=cliente.id,
        produto_id=produto.id,
        data_retirada=hoje,
        data_prevista=hoje + timedelta(days=dias + bonus),
        valor=produto.preco_aluguel,
        multa_paga=0,
        status="ativo",
    )
    produto.estoque -= 1
    db.add(aluguel)
    return aluguel


def registrar(db: Session, dados: schemas.AluguelCriar) -> schemas.Aluguel:
    cliente = _cliente_liberado(db, dados.cliente_id)
    produto = _titulo_disponivel(db, dados.produto_id)
    aluguel = _abrir(db, cliente, produto, dados.dias)
    db.commit()
    db.refresh(aluguel)
    return serializar(aluguel)


def registrar_lote(db: Session, dados: schemas.AluguelLoteCriar) -> list[schemas.Aluguel]:
    """Abre um aluguel por título. Se qualquer um falhar, nenhum é gravado."""
    cliente = _cliente_liberado(db, dados.cliente_id)
    abertos = [
        _abrir(db, cliente, _titulo_disponivel(db, produto_id), dados.dias)
        for produto_id in dados.produto_ids
    ]
    db.commit()
    for aluguel in abertos:
        db.refresh(aluguel)
    return [serializar(a) for a in abertos]


def devolver(db: Session, aluguel_id: int, dados: schemas.Devolucao) -> schemas.Aluguel:
    aluguel = obter(db, aluguel_id)
    if aluguel.status == "devolvido":
        raise HTTPException(409, "Esse aluguel já foi devolvido.")
    data = dados.data_devolucao or date.today()
    if data < aluguel.data_retirada:
        raise HTTPException(400, "A devolução não pode ser anterior à retirada.")

    aluguel.data_devolucao = data
    aluguel.maulta_paga = dados.multa if dados.multa is not None else regras.calcular_multa(aluguel)
    aluguel.status = "devolvido"

    produto = db.get(models.Produto, aluguel.produto_id)
    if produto:
        produto.estoque += 1

    db.commit()
    db.refresh(aluguel)
    return serializar(aluguel)
