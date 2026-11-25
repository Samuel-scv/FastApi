from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.database import Base


class Avaliacao(Base):
  """Nota (1 a 5) e comentário de um cliente sobre um título que ele já alugou ou comprou."""

  __tablename__ = "avaliacoes"
  __table_args__ = (UniqueConstraint("produto_id", "cliente_id", name="uma_avaliacao_por_cliente_e_titulo"),)

  id = Column(Integer, primary_key=True, index=True)
  produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
  cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
  nota = Column(Integer, nullable=False)
  comentario = Column(String, default="")
  criada_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

  produto = relationship("Produto")
  cliente = relationship("Cliente")
