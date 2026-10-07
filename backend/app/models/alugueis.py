from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Aluguel(Base):
    __tablename__ = "alugueis"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    data_retirada = Column(Date, nullable=False)
    data_prevista = Column(Date, nullable=False)
    data_devolucao = Column(Date, nullable=True)
    valor = Column(Float, nullable=False, default=0)
    multa_paga = Column(Float, nullable=False, default=0)
    status = Column(String, nullable=False, default="ativo")  # ativo | devolvido

    cliente = relationship("Cliente", back_populates="alugueis")
    produto = relationship("Produto", back_populates="alugueis")
