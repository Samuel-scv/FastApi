from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class PerguntaCriar(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  texto: str = Field(min_length=5, max_length=500)


class RespostaCriar(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  texto: str = Field(min_length=1, max_length=1000)


class Pergunta(BaseModel):
  id: int
  produto_id: int
  titulo: str
  autor: str  # só o primeiro nome, para não expor dados do cliente na vitrine
  texto: str
  criada_em: datetime
  status: Literal["pendente", "respondida"]
  resposta: Optional[str] = None
  respondida_em: Optional[datetime] = None
  vendedor: Optional[str] = None
