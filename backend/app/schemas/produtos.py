from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(min_length=1)
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
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: Optional[str] = Field(min_length=1, default=None)
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
