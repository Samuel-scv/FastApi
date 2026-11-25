from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Reserva(Base):
  """Fila de espera de um título zerado. A ordem é pela data de criação (FIFO)."""

  __tablename__ = "reservas"

  id = Column(Integer, primary_key=True, index=True)
  produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
  cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
  status = Column(String, nullable=False, default="aguardando")  # aguardando | disponivel | atendida | cancelada
  criada_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
  disponivel_em = Column(DateTime, nullable=True)

  produto = relationship("Produto")
  cliente = relationship("Cliente")
