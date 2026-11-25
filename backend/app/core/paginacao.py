"""Paginação simples por página/tamanho, reaproveitada pelas listagens que podem crescer muito."""
from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy.orm import Query as SQLQuery

T = TypeVar("T")


class Pagina(BaseModel, Generic[T]):
  itens: list[T]
  total: int
  pagina: int
  por_pagina: int
  paginas: int


def parametros(pagina: int = Query(1, ge=1), por_pagina: int = Query(20, ge=1, le=100)) -> tuple[int, int]:
  return pagina, por_pagina


def paginar(query: SQLQuery, pagina: int, por_pagina: int) -> tuple[list, int]:
  total = query.count()
  itens = query.offset((pagina - 1) * por_pagina).limit(por_pagina).all()
  return itens, total


def montar(itens: list, total: int, pagina: int, por_pagina: int) -> dict:
  paginas = max(1, -(-total // por_pagina))  # arredonda para cima
  return {"itens": itens, "total": total, "pagina": pagina, "por_pagina": por_pagina, "paginas": paginas}
