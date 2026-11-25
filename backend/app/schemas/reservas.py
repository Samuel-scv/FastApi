from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReservaCriar(BaseModel):
  cliente_id: int
  produto_id: int


class Reserva(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  produto_id: int
  titulo: str = ""
  cliente_id: int
  cliente: str = ""
  posicao_na_fila: Optional[int] = None  # só enquanto "aguardando"; 1 = o próximo
  status: Literal["aguardando", "disponivel", "atendida", "cancelada"]
  criada_em: datetime
  disponivel_em: Optional[datetime] = None


class AtenderReserva(BaseModel):
  dias: int = Field(ge=1, le=30, default=3)
