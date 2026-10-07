from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..core.database import get_db
from ..services import clientes as service

router = APIRouter(prefix="/clientes", tags=["clientes"])


@router.get("", response_model=list[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db)):
    return service.listar(db)


@router.get("/{cliente_id}", response_model=schemas.Cliente)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return service.serializar(db, service.obter(db, cliente_id))


@router.post("", response_model=schemas.Cliente, status_code=201)
def criar_cliente(dados: schemas.ClienteCriar, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.put("/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, dados: schemas.ClienteAtualizar, db: Session = Depends(get_db)):
    return service.atualizar(db, cliente_id, dados)


@router.delete("/{cliente_id}", status_code=204)
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    service.excluir(db, cliente_id)


@router.post("/{cliente_id}/plano/renovar", response_model=schemas.RenovacaoPlano)
def renovar_plano(cliente_id: int, db: Session = Depends(get_db)):
    return service.renovar_plano(db, cliente_id)


@router.get("/{cliente_id}/historico", response_model=schemas.HistoricoCliente)
def historico_do_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return service.historico(db, cliente_id)
