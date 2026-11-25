from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AvaliacaoCriar(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  nota: int = Field(ge=1, le=5)
  comentario: str = Field(max_length=500, default="")


class Avaliacao(BaseModel):
  id: int
  produto_id: int
  cliente: str  # primeiro nome, como em perguntas
  nota: int
  comentario: str
  criada_em: datetime
