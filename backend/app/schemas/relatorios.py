from datetime import date

from pydantic import BaseModel


class PontoFaturamento(BaseModel):
  data: date
  aluguel: float
  venda: float
  multa: float
  total: float


class Faturamento(BaseModel):
  inicio: date
  fim: date
  total_aluguel: float
  total_venda: float
  total_multa: float
  total_geral: float
  quantidade_alugueis: int
  quantidade_vendas: int
  ticket_medio: float  # total_geral dividido por (alugueis + vendas)
  por_dia: list[PontoFaturamento]


class ItemRanking(BaseModel):
  produto_id: int
  titulo: str
  quantidade: int
  valor: float


class ResumoDashboard(BaseModel):
  faturamento_mes_atual: float
  alugueis_ativos: int
  alugueis_atrasados: int
  titulos_estoque_baixo: int
  titulos_estoque_zerado: int
  perguntas_pendentes: int
  reservas_aguardando: int
  clientes_bloqueados: int
