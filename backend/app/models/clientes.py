from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    email = Column(String, default="")
    telefone = Column(String, default="")
    documento = Column(String, default="")
    endereco = Column(String, default="")
    plano_id = Column(Integer, ForeignKey("planos.id"), nullable=True)
    # Último dia em que a mensalidade vale. Depois dele o plano fica "vencido"
    # e os benefícios (dias extras, carência de multa) deixam de valer.
    plano_vencimento = Column(Date, nullable=True)

    plano = relationship("Plano", back_populates="clientes")
    alugueis = relationship("Aluguel", back_populates="cliente")
    vendas = relationship("Venda", back_populates="cliente")
