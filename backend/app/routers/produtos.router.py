from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("", response_model=list[schemas.Produto])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.Produto).order_by(models.Produto.titulo).all()


@router.get("/{produto_id}", response_model=schemas.Produto)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(models.Produto, produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    return produto


@router.post("", response_model=schemas.Produto, status_code=201)
def criar_produto(dados: schemas.ProdutoCriar, db: Session = Depends(get_db)):
    produto = models.Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.put("/{produto_id}", response_model=schemas.Produto)
def atualizar_produto(produto_id: int, dados: schemas.ProdutoAtualizar, db: Session = Depends(get_db)):
    produto = db.get(models.Produto, produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=204)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.get(models.Produto, produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    em_uso = (
        db.query(models.Aluguel)
        .filter(models.Aluguel.produto_id == produto_id, models.Aluguel.status != "devolvido")
        .first()
    )
    if em_uso:
        raise HTTPException(409, "Há cópia alugada desse título. Receba a devolução antes de excluir.")
    db.delete(produto)
    db.commit()
