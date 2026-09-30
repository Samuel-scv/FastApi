from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/vendas", tags=["vendas"])


@router.get("", response_model=list[schemas.Venda])
def listar_vendas(db: Session = Depends(get_db)):
    return db.query(models.Venda).order_by(models.Venda.data.desc()).all()


@router.get("/{venda_id}", response_model=schemas.Venda)
def obter_venda(venda_id: int, db: Session = Depends(get_db)):
    venda = db.get(models.Venda, venda_id)
    if not venda:
        raise HTTPException(404, "Venda não encontrada.")
    return venda


@router.post("", response_model=schemas.Venda, status_code=201)
def registrar_venda(dados: schemas.VendaCriar, db: Session = Depends(get_db)):
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
    produto.estoque -= dados.quantidade
    db.add(venda)
    db.commit()
    db.refresh(venda)
    return venda
