from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TipoMovimento = Literal["inicial", "entrada", "aluguel", "devolucao", "venda", "perda", "ajuste"]


class EntradaEstoque(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  quantidade: int = Field(ge=1)
  motivo: str = ""  # ex.: "compra do fornecedor", "doação"


class PerdaEstoque(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  quantidade: int = Field(ge=1)
  motivo: str = Field(min_length=1)  # ex.: "fita mastigada", "disco riscado", "extravio"


class AjusteEstoque(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  saldo: int = Field(ge=0)  # contagem real na prateleira
  motivo: str = Field(min_length=1)  # ex.: "inventário de novembro"


class MovimentoEstoque(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  produto_id: int
  titulo: str = ""
  tipo: TipoMovimento
  quantidade: int
  saldo_apos: int
  motivo: str
  usuario_id: Optional[int] = None
  aluguel_id: Optional[int] = None
  venda_id: Optional[int] = None
  criado_em: datetime


class ItemEstoque(BaseModel):
  produto_id: int
  titulo: str
  tipo: str
  disponivel: int  # na prateleira, prontas para alugar/vender
  alugadas: int  # na rua
  total_acervo: int  # disponivel + alugadas
  estoque_minimo: int
  situacao: Literal["ok", "baixo", "zerado"]  # calculada sobre o total_acervo
  todas_alugadas: bool  # tem acervo, mas nenhuma cópia na prateleira agora


class ResumoEstoque(BaseModel):
  titulos: int
  copias_disponiveis: int
  copias_alugadas: int
  titulos_baixos: int
  titulos_zerados: int
  itens: list[ItemEstoque]
