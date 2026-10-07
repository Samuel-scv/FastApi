from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Plano(Base):
    __tablename__ = "planos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco_mensal = Column(Float, nullable=False, default=0)
    limite_mensal = Column(Integer, nullable=False, default=1)
    beneficios = Column(Text, default="")
    dias_bonus = Column(Integer, default=0)           # dias extras de prazo
    carencia_multa_dias = Column(Integer, default=0)  # dias de atraso perdoados antes de multar

    clientes = relationship("Cliente", back_populates="plano")
