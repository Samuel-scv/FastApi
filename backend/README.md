# Video Locadora Galaxia — API

Backend em **FastAPI** da videolocadora: acervo de produtos, clientes, planos de
assinatura, aluguéis (com prazo e multa por atraso) e vendas definitivas.

## Como rodar

```bash
cd backend
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`. Swagger em `http://127.0.0.1:8000/docs`.

No primeiro start o banco `galaxia.db` (SQLite) é criado e populado com produtos,
planos e clientes de exemplo. Para voltar ao estado inicial, apague o `galaxia.db`
e suba de novo.

## Testes

```bash
pip install -r requirements-dev.txt
python -m pytest
```

Os testes usam um banco em memória e não mexem no `galaxia.db`.

## Configuração (.env)

Opcional — copie o `.env.example` para `.env`. Sem ele valem os padrões.

| Chave           | Padrão               | O que controla                     |
|-----------------|----------------------|------------------------------------|
| `DATABASE_URL`  | `sqlite:///./galaxia.db` | banco de dados                 |
| `CORS_ORIGINS`  | `*`                  | origens liberadas (separe por vírgula) |
| `MULTA_POR_DIA` | `3.5`                | multa por dia de atraso (R$)       |
| `DIAS_PLANO`    | `30`                 | duração de cada mensalidade (dias) |

## Estrutura

```
backend/
  app/
    main.py              # cria o app, CORS, registra os routers
    regras.py            # regras de negócio puras: multa, bloqueio, plano vigente
    core/
      config.py          # lê o .env
      database.py        # engine, sessão e get_db
    models/              # tabelas SQLAlchemy (um arquivo por entidade)
    schemas/             # validação e serialização (Pydantic)
    services/            # lógica de cada módulo (consulta, valida, grava)
    routers/             # só HTTP: recebe a requisição e chama o service
    seeds/
      dados_iniciais.py  # dados de exemplo do primeiro start
  tests/
```

Fluxo de uma requisição: `router → service → (regras + models) → schema de resposta`.

## Regras de negócio

- **Estoque:** alugar ou vender sem cópia disponível retorna 409. A devolução repõe 1 cópia.
- **Bloqueio:** cliente com aluguel em atraso não abre novo aluguel (409).
- **Multa:** `MULTA_POR_DIA` por dia de atraso, calculada até a devolução. O balcão pode
  informar outro valor em `multa` na devolução (ex.: `0` para perdoar).
- **Plano:** vale até `plano_vencimento` (`plano_status`: `sem_plano`, `ativo` ou `vencido`).
  Assinar ou trocar de plano define o vencimento para hoje + `DIAS_PLANO`;
  `POST /clientes/{id}/plano/renovar` cobra a próxima mensalidade. Plano vencido perde
  `dias_bonus` e `carencia_multa_dias` até renovar.
- **Limite mensal:** não bloqueia. `limite_atingido` avisa que a próxima locação é avulsa.
- **Aluguel em lote:** `POST /alugueis/lote` leva vários títulos de uma vez — se um
  falhar, nenhum é gravado.
- **Venda:** baixa definitiva no estoque, sem devolução. `GET /vendas/{id}/comprovante`
  devolve os dados do comprovante.
- **Exclusão:** cliente ou título com aluguel em aberto **ou** com histórico não pode ser
  excluído (409). Para tirar um título de circulação, zere o estoque.

A lista completa de rotas está em [`../rotas.md`](../rotas.md).
