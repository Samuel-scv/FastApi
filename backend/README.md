# Video Locadora Galaxia — API

Backend em **FastAPI** para a videolocadora: acervo de produtos, clientes,
planos de assinatura, aluguéis (com prazo e multa por atraso) e vendas
definitivas. Segue o mesmo modelo de dados usado nos frontends já prontos
(o painel administrativo e a versão "anos 90").

## Como rodar

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. Documentação interativa (Swagger) em
`http://127.0.0.1:8000/docs`.

No primeiro start, o banco `galaxia.db` (SQLite, criado automaticamente) é
populado com produtos, planos e clientes de exemplo — os mesmos títulos que
já aparecem nos frontends.

## Conectar ao painel administrativo / site anos 90

Os frontends já têm uma aba/campo para apontar para a API. Basta colocar
`http://127.0.0.1:8000` lá. O CORS já vem liberado (`allow_origins=["*"]`).

## Estrutura

```
backend/
  app/
    main.py            # cria o app, registra rotas, popula dados de exemplo
    database.py         # engine e sessão do SQLAlchemy (SQLite)
    models.py            # tabelas: Produto, Cliente, Plano, Aluguel, Venda
    schemas.py            # validação/serialização (Pydantic)
    regras.py              # regras de negócio: multa, bloqueio, limite de plano
    dados_iniciais.py       # dados de exemplo carregados no primeiro start
    routers/
      produtos.py
      clientes.py
      planos.py
      alugueis.py
      vendas.py
  requirements.txt
```

## Regras de negócio implementadas

- **Estoque**: alugar ou vender sem cópia disponível retorna erro 409.
- **Bloqueio**: cliente com aluguel em atraso não pode abrir novo aluguel.
- **Multa**: R$ 3,50 por dia de atraso (constante `MULTA_POR_DIA` em
  `app/regras.py`), calculada automaticamente até a data de devolução.
- **Planos**: cada plano pode dar dias extras de prazo (`dias_bonus`) ou
  carência de multa (`carencia_multa_dias`); o limite mensal de locações
  (`limite_mensal`) é informado no cliente (`locacoes_no_mes`), mas não
  bloqueia — cabe ao balconista decidir se cobra como avulso.
- **Venda**: dá baixa definitiva no estoque, sem geração de devolução.

## Rotas

| Método | Rota                          | Descrição                              |
|--------|-------------------------------|-----------------------------------------|
| GET    | `/produtos`                   | lista o acervo                          |
| POST   | `/produtos`                   | cadastra um título                      |
| PUT    | `/produtos/{id}`              | atualiza título e estoque               |
| DELETE | `/produtos/{id}`              | remove do acervo                        |
| GET    | `/clientes`                   | lista clientes (com bloqueado/uso do mês)|
| POST   | `/clientes`                   | cadastra cliente                        |
| PUT    | `/clientes/{id}`              | atualiza cadastro e plano               |
| DELETE | `/clientes/{id}`              | remove cliente                          |
| GET    | `/alugueis`                   | lista locações (?status=ativo/devolvido)|
| POST   | `/alugueis`                   | abre locação (baixa 1 do estoque)       |
| POST   | `/alugueis/{id}/devolucao`    | recebe de volta e calcula multa         |
| GET    | `/vendas`                     | lista vendas                            |
| POST   | `/vendas`                     | registra venda (baixa definitiva)       |
| GET    | `/planos`                     | lista planos                            |
| POST   | `/planos`                     | cria plano                              |
| PUT    | `/planos/{id}`                | atualiza plano                          |
| DELETE | `/planos/{id}`                | remove plano                            |
