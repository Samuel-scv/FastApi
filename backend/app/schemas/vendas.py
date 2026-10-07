from datetime import date

from pydantic import BaseModel, ConfigDict, Field


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


class ComprovanteVenda(BaseModel):
    venda_id: int
    data: date
    cliente: str
    titulo: str
    quantidade: int
    preco_unitario: float
    valor_total: float
