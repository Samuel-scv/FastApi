from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey, Text, Date
)
from sqlalchemy.orm import relationship

from .database import Base


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
    estoque = Column(Integer, nullable=False, default=0)

    alugueis = relationship("Aluguel", back_populates="produto")
    vendas = relationship("Venda", back_populates="produto")


class Plano(Base):
    __tablename__ = "planos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco_mensal = Column(Float, nullable=False, default=0)
    limite_mensal = Column(Integer, nullable=False, default=1)
    beneficios = Column(Text, default="")
    dias_bonus = Column(Integer, default=0)        # dias extras de prazo
    carencia_multa_dias = Column(Integer, default=0)  # dias de atraso perdoados antes de multar

    clientes = relationship("Cliente", back_populates="plano")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False, index=True)
    email = Column(String, default="")
    telefone = Column(String, default="")
    documento = Column(String, default="")
    endereco = Column(String, default="")
    plano_id = Column(Integer, ForeignKey("planos.id"), nullable=True)

    plano = relationship("Plano", back_populates="clientes")
    alugueis = relationship("Aluguel", back_populates="cliente")
    vendas = relationship("Venda", back_populates="cliente")


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


class Venda(Base):
    __tablename__ = "vendas"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    valor_total = Column(Float, nullable=False, default=0)
    data = Column(Date, nullable=False)

    cliente = relationship("Cliente", back_populates="vendas")
    produto = relationship("Produto", back_populates="vendas")
