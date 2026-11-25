# Importar todos os models aqui garante que o SQLAlchemy conheça todas as
# tabelas (e as relações entre elas) antes do create_all.
from .alugueis import Aluguel
from .avaliacoes import Avaliacao
from .clientes import Cliente
from .estoque import MovimentoEstoque
from .favoritos import Favorito
from .perguntas import Pergunta
from .reservas import Reserva
from .planos import Plano
from .produtos import Produto
from .usuarios import Usuario
from .vendas import Venda

__all__ = ["Aluguel", "Avaliacao", "Cliente", "Favorito", "MovimentoEstoque", "Pergunta", "Reserva", "Plano", "Produto", "Usuario", "Venda"]
