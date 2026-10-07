from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas


def listar(db: Session) -> list[models.Produto]:
    return db.query(models.Produto).order_by(models.Produto.titulo).all()


def obter(db: Session, produto_id: int) -> models.Produto:
    produto = db.get(models.Produto, produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    return produto


def criar(db: Session, dados: schemas.ProdutoCriar) -> models.Produto:
    produto = models.Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


def atualizar(db: Session, produto_id: int, dados: schemas.ProdutoAtualizar) -> models.Produto:
    produto = obter(db, produto_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


def excluir(db: Session, produto_id: int) -> None:
    produto = obter(db, produto_id)
    alugado = (
        db.query(models.Aluguel)
        .filter(models.Aluguel.produto_id == produto_id, models.Aluguel.status != "devolvido")
        .first()
    )
    if alugado:
        raise HTTPException(409, "Há cópia alugada desse título. Receba a devolução antes de excluir.")
    tem_historico = (
        db.query(models.Aluguel).filter(models.Aluguel.produto_id == produto_id).first()
        or db.query(models.Venda).filter(models.Venda.produto_id == produto_id).first()
    )
    if tem_historico:
        raise HTTPException(
            409, "Esse título tem aluguéis/vendas no histórico e não pode ser excluído. Zere o estoque."
        )
    db.delete(produto)
    db.commit()
