from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..core.database import get_db
from ..services import vendas as service

router = APIRouter(prefix="/vendas", tags=["vendas"])


@router.get("", response_model=list[schemas.Venda])
def listar_vendas(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get("/{venda_id}", response_model=schemas.Venda)
def obter_venda(venda_id: int, db: Session = Depends(get_db)):
    return service.obter(db, venda_id)


@router.get("/{venda_id}/comprovante", response_model=schemas.ComprovanteVenda)
def comprovante_da_venda(venda_id: int, db: Session = Depends(get_db)):
    return service.comprovante(db, venda_id)


@router.post("", response_model=schemas.Venda, status_code=201)
def registrar_venda(dados: schemas.VendaCriar, db: Session = Depends(get_db)):
    return service.registrar(db, dados)
