from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .alugueis import Aluguel
from .vendas import Venda


class ClienteBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1)
    email: str = ""
    telefone: str = ""
    documento: str = ""
    endereco: str = ""
    plano_id: Optional[int] = None


class ClienteCriar(ClienteBase):
    pass


class ClienteAtualizar(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: Optional[str] = Field(min_length=1, default=None)
    email: Optional[str] = None
    telefone: Optional[str] = None
    documento: Optional[str] = None
    endereco: Optional[str] = None
    plano_id: Optional[int] = None


class Cliente(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    plano_vencimento: Optional[date] = None
    plano_status: str = "sem_plano"      # sem_plano | ativo | vencido
    bloqueado: bool = False              # tem aluguel em atraso
    locacoes_no_mes: int = 0
    limite_mensal: Optional[int] = None  # do plano vigente
    limite_atingido: bool = False


class RenovacaoPlano(BaseModel):
    cliente_id: int
    plano: str
    valor_cobrado: float
    vencimento_anterior: Optional[date] = None
    novo_vencimento: date


class HistoricoCliente(BaseModel):
    cliente: Cliente
    alugueis: list[Aluguel]
    vendas: list[Venda]
