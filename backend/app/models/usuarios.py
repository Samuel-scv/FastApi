from sqlalchemy import Boolean, Column, Integer, String

from ..core.database import Base


class Usuario(Base):
  __tablename__ = "usuarios"

  id = Column(Integer, primary_key=True, index=True)
  nome = Column(String, nullable=False)
  email = Column(String, nullable=False, unique=True, index=True)
  senha_hash = Column(String, nullable=False)
  ativo = Column(Boolean, nullable=False, default=True)
  admin = Column(Boolean, nullable=False, default=False)
  vendedor = Column(Boolean, nullable=False, default=False)  # equipe da loja; cliente comum = ambos falsos
