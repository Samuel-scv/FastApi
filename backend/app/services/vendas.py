from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas


def listar(db: Session) -> list[models.Venda]:
    return db.query(models.Venda).order_by(models.Venda.data.desc(), models.Venda.id.desc()).all()


def obter(db: Session, venda_id: int) -> models.Venda:
    venda = db.get(models.Venda, venda_id)
    if not venda:
        raise HTTPException(404, "Venda não encontrada.")
    return venda


def registrar(db: Session, dados: schemas.VendaCriar) -> models.Venda:
    cliente = db.get(models.Cliente, dados.cliente_id)
    if not cliente:
        raise HTTPException(404, "Cliente não encontrado.")
    produto = db.get(models.Produto, dados.produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    if produto.estoque < dados.quantidade:
        raise HTTPException(
            409, f"Só há {produto.estoque} cópia(s) de '{produto.titulo}' em estoque."
        )

    venda = models.Venda(
        cliente_id=cliente.id,
        produto_id=produto.id,
        quantidade=dados.quantidade,
        valor_total=round(produto.preco_venda * dados.quantidade, 2),
        data=date.today(),
    )
    produto.estoque -= dados.quantidade  # baixa definitiva, sem devolução
    db.add(venda)
    db.commit()
    db.refresh(venda)
    return venda


def comprovante(db: Session, venda_id: int) -> schemas.ComprovanteVenda:
    venda = obter(db, venda_id)
    return schemas.ComprovanteVenda(
        venda_id=venda.id,
        data=venda.data,
        cliente=venda.cliente.nome,
        titulo=venda.produto.titulo,
        quantidade=venda.quantidade,
        preco_unitario=round(venda.valor_total / venda.quantidade, 2),
        valor_total=venda.valor_total,
    )
