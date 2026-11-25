from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from ..core.database import Base


class Favorito(Base):
  __tablename__ = "favoritos"
  __table_args__ = (UniqueConstraint("usuario_id", "produto_id", name="um_favorito_por_usuario_e_titulo"),)

  id = Column(Integer, primary_key=True, index=True)
  usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
  produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False, index=True)
  criado_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

  produto = relationship("Produto")
