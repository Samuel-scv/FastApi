from datetime import datetime

from pydantic import BaseModel


class Favorito(BaseModel):
  id: int
  produto_id: int
  titulo: str
  criado_em: datetime
