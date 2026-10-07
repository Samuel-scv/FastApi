from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PlanoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1)
    preco_mensal: float = Field(ge=0, default=0)
    limite_mensal: int = Field(ge=1, default=1)
    beneficios: str = ""
    dias_bonus: int = Field(ge=0, default=0)
    carencia_multa_dias: int = Field(ge=0, default=0)


class PlanoCriar(PlanoBase):
    pass


class PlanoAtualizar(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: Optional[str] = Field(min_length=1, default=None)
    preco_mensal: Optional[float] = Field(ge=0, default=None)
    limite_mensal: Optional[int] = Field(ge=1, default=None)
    beneficios: Optional[str] = None
    dias_bonus: Optional[int] = Field(ge=0, default=None)
    carencia_multa_dias: Optional[int] = Field(ge=0, default=None)


class Plano(PlanoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
