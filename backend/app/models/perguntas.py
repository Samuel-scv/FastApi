from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Pergunta(Base):
  """Pergunta de um cliente sobre um título; um vendedor responde uma vez."""

  __tablename__ = "perguntas"

  id = Column(Integer, primary_key=True, index=True)
  produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
  autor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
  texto = Column(String, nullable=False)
  criada_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
  resposta = Column(Text, nullable=True)
  respondida_em = Column(DateTime, nullable=True)
  vendedor_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

  produto = relationship("Produto")
  autor = relationship("Usuario", foreign_keys=[autor_id])
  vendedor = relationship("Usuario", foreign_keys=[vendedor_id])
