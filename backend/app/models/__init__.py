# Importar todos os models aqui garante que o SQLAlchemy conheça todas as
# tabelas (e as relações entre elas) antes do create_all.
from .alugueis import Aluguel
from .clientes import Cliente
from .planos import Plano
from .produtos import Produto
from .vendas import Venda

__all__ = ["Aluguel", "Cliente", "Plano", "Produto", "Venda"]
