from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..core.auth import exigir_admin, exigir_vendedor
from ..core.paginacao import Pagina
from ..core.database import get_db
from ..services import clientes as service

router = APIRouter(prefix="/clientes", tags=["clientes"], dependencies=[Depends(exigir_vendedor)])


@router.get("", response_model=Pagina[schemas.Cliente])
def listar_clientes(pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100), q: str | None = None, db: Session = Depends(get_db)):
    """`q` busca por nome."""
    return service.listar(db, pagina, por_pagina, q)


@router.get("/{cliente_id}", response_model=schemas.Cliente)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return service.serializar(db, service.obter(db, cliente_id))


@router.post("", response_model=schemas.Cliente, status_code=201)
def criar_cliente(dados: schemas.ClienteCriar, db: Session = Depends(get_db)):
    return service.criar(db, dados)


@router.put("/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, dados: schemas.ClienteAtualizar, db: Session = Depends(get_db)):
    return service.atualizar(db, cliente_id, dados)


@router.delete("/{cliente_id}", status_code=204, dependencies=[Depends(exigir_admin)])
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    service.excluir(db, cliente_id)


@router.post("/{cliente_id}/vincular-usuario", response_model=schemas.Cliente)
def vincular_usuario(cliente_id: int, dados: schemas.VincularUsuario, db: Session = Depends(get_db)):
    """Liga este cadastro de balcão à conta de login do cliente no site (para ele poder avaliar/favoritar)."""
    return service.vincular_usuario(db, cliente_id, dados)


@router.post("/{cliente_id}/plano/renovar", response_model=schemas.RenovacaoPlano)
def renovar_plano(cliente_id: int, db: Session = Depends(get_db)):
    return service.renovar_plano(db, cliente_id)


@router.get("/{cliente_id}/historico", response_model=schemas.HistoricoCliente)
def historico_do_cliente(cliente_id: int, db: Session = Depends(get_db)):
    return service.historico(db, cliente_id)
