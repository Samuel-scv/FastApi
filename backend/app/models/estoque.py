from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class MovimentoEstoque(Base):
  """Uma linha por mudança no estoque da prateleira. Nunca é editada nem apagada: é o histórico."""

  __tablename__ = "movimentos_estoque"

  id = Column(Integer, primary_key=True, index=True)
  produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
  tipo = Column(String, nullable=False)  # inicial | entrada | aluguel | devolucao | venda | perda | ajuste
  quantidade = Column(Integer, nullable=False)  # com sinal: +3 entrou, -1 saiu
  saldo_apos = Column(Integer, nullable=False)
  motivo = Column(String, nullable=False, default="")
  usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)  # vazio quando é automático (aluguel/venda)
  aluguel_id = Column(Integer, ForeignKey("alugueis.id"), nullable=True)
  venda_id = Column(Integer, ForeignKey("vendas.id"), nullable=True)
  criado_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

  produto = relationship("Produto")
