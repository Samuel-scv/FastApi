from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AluguelCriar(BaseModel):
    cliente_id: int
    produto_id: int
    dias: int = Field(ge=1, le=30, default=3)


class AluguelLoteCriar(BaseModel):
    """Um cliente levando vários títulos de uma vez (tudo ou nada)."""
    cliente_id: int
    produto_ids: list[int] = Field(min_length=1, max_length=10)
    dias: int = Field(ge=1, le=30, default=3)


class Devolucao(BaseModel):
    data_devolucao: Optional[date] = None
    multa: Optional[float] = Field(ge=0, default=None)  # sobrescreve a multa calculada


class Aluguel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    produto_id: int
    data_retirada: date
    data_prevista: date
    data_devolucao: Optional[date] = None
    valor: float
    multa_paga: float
    status: str
    dias_atraso: int = 0
    multa_estimada: float = 0
