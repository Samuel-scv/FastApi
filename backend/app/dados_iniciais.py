from datetime import date, timedelta

from sqlalchemy.orm import Session

from . import models


def popular_se_vazio(db: Session) -> None:
    if db.query(models.Produto).first():
        return  # já tem dados, não sobrescreve

    produtos = [
        models.Produto(titulo="Cidade de Deus", diretor="Fernando Meirelles", genero="Drama",
                        classificacao="16", ano=2002, preco_aluguel=8.9, preco_venda=39.9, estoque=4,
                        sinopse="Dois garotos da Cidade de Deus seguem caminhos opostos."),
        models.Produto(titulo="Bacurau", diretor="Kleber Mendonça Filho", genero="Suspense",
                        classificacao="16", ano=2019, preco_aluguel=9.9, preco_venda=44.9, estoque=3,
                        sinopse="Um povoado do sertão some do mapa e recebe visitas nada amistosas."),
        models.Produto(titulo="O Auto da Compadecida", diretor="Guel Arraes", genero="Comédia",
                        classificacao="12", ano=2000, preco_aluguel=7.5, preco_venda=34.9, estoque=5,
                        sinopse="João Grilo e Chicó aprontam golpes no sertão até serem julgados no céu."),
        models.Produto(titulo="Central do Brasil", diretor="Walter Salles", genero="Drama",
                        classificacao="12", ano=1998, preco_aluguel=7.5, preco_venda=32.9, estoque=2,
                        sinopse="Uma escrevente de cartas atravessa o país com um menino em busca do pai."),
        models.Produto(titulo="Tropa de Elite", diretor="José Padilha", genero="Ação",
                        classificacao="18", ano=2007, preco_aluguel=8.9, preco_venda=37.9, estoque=0,
                        sinopse="O capitão Nascimento procura um substituto antes de deixar o BOPE."),
    ]
    db.add_all(produtos)

    planos = [
        models.Plano(nome="Prateleira", preco_mensal=24.9, limite_mensal=3,
                     beneficios="3 locações por mês, sem taxa de reserva"),
        models.Plano(nome="Sessão dupla", preco_mensal=39.9, limite_mensal=6, dias_bonus=1,
                     beneficios="6 locações por mês e 1 dia extra de prazo"),
        models.Plano(nome="Maratona", preco_mensal=69.9, limite_mensal=15, carencia_multa_dias=1,
                     beneficios="15 locações por mês, sem multa no primeiro dia de atraso"),
    ]
    db.add_all(planos)
    db.flush()  # garante os ids antes de referenciar em clientes

    clientes = [
        models.Cliente(nome="Marina Prado", email="marina@email.com", telefone="(18) 99712-4408",
                        documento="321.554.880-11", endereco="Araçatuba/SP", plano_id=planos[1].id),
        models.Cliente(nome="Otávio Bandeira", email="otavio@email.com", telefone="(18) 99120-7733",
                        documento="118.902.446-30", endereco="Araçatuba/SP", plano_id=None),
        models.Cliente(nome="Cléo Nakamura", email="cleo@email.com", telefone="(18) 98844-1290",
                        documento="455.019.223-07", endereco="Birigui/SP", plano_id=planos[0].id),
    ]
    db.add_all(clientes)
    db.flush()

    hoje = date.today()
    alugueis = [
        models.Aluguel(cliente_id=clientes[0].id, produto_id=produtos[2].id,
                        data_retirada=hoje - timedelta(days=9), data_prevista=hoje - timedelta(days=4),
                        valor=7.5, status="ativo"),
        models.Aluguel(cliente_id=clientes[1].id, produto_id=produtos[0].id,
                        data_retirada=hoje - timedelta(days=2), data_prevista=hoje + timedelta(days=1),
                        valor=8.9, status="ativo"),
    ]
    db.add_all(alugueis)

    db.commit()
