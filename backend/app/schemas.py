from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------- Produto ----------
class ProdutoBase(BaseModel):
    titulo: str
    diretor: str = ""
    genero: str = ""
    classificacao: str = "L"
    ano: Optional[int] = None
    sinopse: str = ""
    preco_aluguel: float = Field(ge=0, default=0)
    preco_venda: float = Field(ge=0, default=0)
    estoque: int = Field(ge=0, default=0)


class ProdutoCriar(ProdutoBase):
    pass


class ProdutoAtualizar(BaseModel):
    titulo: Optional[str] = None
    diretor: Optional[str] = None
    genero: Optional[str] = None
    classificacao: Optional[str] = None
    ano: Optional[int] = None
    sinopse: Optional[str] = None
    preco_aluguel: Optional[float] = Field(ge=0, default=None)
    preco_venda: Optional[float] = Field(ge=0, default=None)
    estoque: Optional[int] = Field(ge=0, default=None)


class Produto(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Plano ----------
class PlanoBase(BaseModel):
    nome: str
    preco_mensal: float = Field(ge=0, default=0)
    limite_mensal: int = Field(ge=1, default=1)
    beneficios: str = ""
    dias_bonus: int = Field(ge=0, default=0)
    carencia_multa_dias: int = Field(ge=0, default=0)


class PlanoCriar(PlanoBase):
    pass


class PlanoAtualizar(BaseModel):
    nome: Optional[str] = None
    preco_mensal: Optional[float] = Field(ge=0, default=None)
    limite_mensal: Optional[int] = Field(ge=1, default=None)
    beneficios: Optional[str] = None
    dias_bonus: Optional[int] = Field(ge=0, default=None)
    carencia_multa_dias: Optional[int] = Field(ge=0, default=None)


class Plano(PlanoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Cliente ----------
class ClienteBase(BaseModel):
    nome: str
    email: str = ""
    telefone: str = ""
    documento: str = ""
    endereco: str = ""
    plano_id: Optional[int] = None


class ClienteCriar(ClienteBase):
    pass


class ClienteAtualizar(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    documento: Optional[str] = None
    endereco: Optional[str] = None
    plano_id: Optional[int] = None


class Cliente(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bloqueado: bool = False
    locacoes_no_mes: int = 0


# ---------- Aluguel ----------
class AluguelCriar(BaseModel):
    cliente_id: int
    produto_id: int
    dias: int = Field(ge=1, default=3)


class Devolucao(BaseModel):
    data_devolucao: Optional[date] = None
    multa: Optional[float] = Field(ge=0, default=None)


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


# ---------- Venda ----------
class VendaCriar(BaseModel):
    cliente_id: int
    produto_id: int
    quantidade: int = Field(ge=1, default=1)


class Venda(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    produto_id: int
    quantidade: int
    valor_total: float
    data: date
