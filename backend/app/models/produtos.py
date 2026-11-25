from sqlalchemy import Column, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from ..core.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, nullable=False, index=True)
    diretor = Column(String, default="")
    genero = Column(String, default="")
    classificacao = Column(String, default="L")
    ano = Column(Integer, default=None)
    sinopse = Column(Text, default="")
    preco_aluguel = Column(Float, nullable=False, default=0)
    preco_venda = Column(Float, nullable=False, default=0)
    estoque = Column(Integer, nullable=False, default=0)  # cópias na prateleira; só muda via services/estoque.py
    tipo = Column(String, nullable=False, default="filme")  # filme | serie
    temporadas = Column(Integer, nullable=True)  # só para séries
    estoque_minimo = Column(Integer, nullable=False, default=1)  # abaixo disso o título aparece como "baixo"

    alugueis = relationship("Aluguel", back_populates="produto")
    vendas = relationship("Venda", back_populates="produto")
