from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..core.database import get_db
from ..services import produtos as service

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("", response_model=list[schemas.Produto])
def listar_produtos(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get("/{produto_id}", response_model=schemas.Produto)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    return service.obter(db, produto_id)


@router.post("", response_model=schemas.Produto, status_code=201)
def criar_produto(dados: schemas.ProdutoCriar, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.put("/{produto_id}", response_model=schemas.Produto)
def atualizar_produto(produto_id: int, dados: schemas.ProdutoAtualizar, db: Session = Depends(get_db)):
    return service.atualizar(db, produto_id, dados)


@router.delete("/{produto_id}", status_code=204)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    service.excluir(db, produto_id)
