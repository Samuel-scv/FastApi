from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from .. import schemas
from ..core.auth import exigir_vendedor
from ..core.database import get_db
from ..services import relatorios as service

router = APIRouter(prefix="/relatorios", tags=["relatorios"], dependencies=[Depends(exigir_vendedor)])


@router.get("/faturamento", response_model=schemas.Faturamento)
def faturamento(inicio: date | None = None, fim: date | None = None, db: Session = Depends(get_db)):
  """Sem datas, usa o mês atual."""
  return service.faturamento(db, inicio, fim)


@router.get("/mais-alugados", response_model=list[schemas.ItemRanking])
def mais_alugados(limite: int = Query(10, ge=1, le=50), inicio: date | None = None, fim: date | None = None, db: Session = Depends(get_db)):
  return service.mais_alugados(db, limite, inicio, fim)


@router.get("/mais-vendidos", response_model=list[schemas.ItemRanking])
def mais_vendidos(limite: int = Query(10, ge=1, le=50), inicio: date | None = None, fim: date | None = None, db: Session = Depends(get_db)):
  return service.mais_vendidos(db, limite, inicio, fim)


@router.get("/dashboard", response_model=schemas.ResumoDashboard)
def dashboard(db: Session = Depends(get_db)):
  """Visão geral para abrir a tela inicial do balcão."""
  return service.dashboard(db)
