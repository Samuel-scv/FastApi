# Plano de testes

## Escopo analisado

A solicitação menciona os diretórios web e api, mas eles não existem neste repositório. A estrutura real é frontend (React/Vite) e backend (FastAPI); o plano abaixo considera esses caminhos e as regras de [AGENTS.md](AGENTS.md). Este documento planeja os testes; não foram feitas alterações de código.

## Cinco funcionalidades mais críticas

| Prioridade | Funcionalidade | Caminho feliz | Erro esperado | Caso de borda |
|---|---|---|---|---|
| 1 — Bloqueadora | Inicialização da API e carregamento do catálogo no frontend | Iniciar a aplicação e exibir títulos e estoque no catálogo. **Ponta a ponta** | Uma chamada da API falha: mostrar erro e permitir tentar novamente, sem deixar a tela travada. **Componente (tela)** | Banco vazio deve ser inicializado/semeado; banco já populado não deve receber dados iniciais duplicados. **Integração (API/lifespan)** |
| 2 — Crítica | Identificar/criar cliente e alugar fita | Cliente existente ou recém-cadastrado aluga título disponível; prazo aparece e estoque diminui. **Ponta a ponta** | Cliente bloqueado, produto inexistente ou sem estoque: operação recusada e estado preservado. **Integração (API)** | Normalizar telefone com/sem formatação e tentar alugar o último exemplar; não permitir estoque negativo. **Integração (API)** |
| 3 — Crítica | Devolver fita e liquidar eventual multa | Devolução altera status, repõe uma unidade e registra multa zero quando não há atraso. **Ponta a ponta** | Aluguel inexistente ou já devolvido deve ser recusado sem repor estoque novamente. **Integração (API)** | Vencimento hoje, atraso com carência e devolução anterior à retirada; confirmar cálculo e persistência exata da multa. **Integração (API)** |
| 4 — Alta | Assinar/renovar plano e aplicar benefícios | Associar plano, mostrar vigência e aplicar dias de bônus no próximo aluguel. **Ponta a ponta** | Renovação sem plano ou associação de plano inexistente deve retornar erro controlado, sem alterar o cliente. **Integração (API)** | Plano vencendo hoje ou já vencido: validar vigência, renovação e interrupção dos benefícios no limite da data. **Integração (API)** |
| 5 — Alta para operação | Registrar venda, atualizar estoque e emitir comprovante | Venda válida calcula total, reduz estoque e retorna comprovante com cliente, produto, quantidade e preço. **Integração (API)** | Produto/cliente inexistente ou quantidade acima do estoque: recusar sem gravar venda ou alterar saldo. **Integração (API)** | Vender exatamente todo o estoque e validar quantidade mínima e valores decimais no total/comprovante. **Integração (API)** |

> A venda é crítica para a operação da API, mas não há tela de venda no frontend atualmente; por isso, seus testes propostos são de integração da API, não de ponta a ponta pelo navegador.

## Ferramentas recomendadas

| Camada | Framework/versão declarada | Ferramenta recomendada | Observação |
|---|---|---|---|
| API | FastAPI `>=0.110`; pytest `>=8`; httpx `>=0.27` ([backend/requirements.txt](backend/requirements.txt), [backend/requirements-dev.txt](backend/requirements-dev.txt)) | **pytest + `fastapi.testclient.TestClient`** | As dependências e 25 testes de API já existem. Usar o cliente HTTP síncrono para verificar endpoints, status, persistência e efeitos no estoque. |
| Frontend | React `^19.0.0`; Vite `^6.0.0` | **Vitest + React Testing Library** | Não há ferramenta ou script de teste no frontend. Vitest integra-se ao Vite; Testing Library valida o comportamento visível dos componentes sem depender da implementação interna. |
| Fluxos completos | Frontend React/Vite + API FastAPI | **Playwright** | Reservar para poucos fluxos críticos no navegador, como catálogo → aluguel → devolução, usando os serviços reais de teste. |

As versões acima são as faixas declaradas nos arquivos de dependências; não representam necessariamente as versões instaladas. O [package.json](package.json) da raiz não define o framework de frontend e seu script `test` é apenas um placeholder que falha. O [package.json do frontend](frontend/package.json) é o relevante para essa aplicação.

## Ajustes necessários para melhorar a testabilidade

| Área | Ajuste recomendado | Motivo/observação |
|---|---|---|
| Inicialização da API | Testar o `lifespan` explicitamente com `TestClient` em contexto (`with`) e banco isolado; manter separados os testes de endpoints que não precisam iniciar a aplicação. | O fixture atual em [conftest.py](backend/tests/conftest.py) usa `TestClient` sem contexto e documenta que não executa o `lifespan`; criação de tabelas, migração SQLite e seed ficam sem cobertura. FastAPI já expõe `app` separadamente — não há `app.listen` de Express para separar. |
| Dependências de teste | Garantir que cada teste reverta/limpe `app.dependency_overrides` e encerre sessão e engine, inclusive quando falhar. | Evita vazamento de configuração ou conexão entre testes. |
| Regras de data | Injetar um relógio/fonte de data nas regras de aluguel e planos. | Permite testar vencimento, carência, multa e renovação em datas determinísticas, sem alterar diretamente os registros do banco no teste. |
| Devolução/multa | Corrigir a atribuição identificada no serviço: `maulta_paga` parece ser um erro de digitação; modelo e schema usam `multa_paga`. Acrescentar/confirmar teste de atraso que confira resposta e valor persistido. | Há teste que espera multa de R$ 14,00, mas o serviço atribui a um atributo com nome divergente. É um risco de regressão funcional a resolver antes de confiar nessa cobertura. |
| CORS em desenvolvimento | Conferir a origem configurada para a API em [compose.yaml](compose.yaml): o frontend é publicado em `5173`, enquanto a origem CORS indicada para dev é `8080`; preservar `http://localhost:5173` conforme [AGENTS.md](AGENTS.md). | Uma origem incorreta pode impedir as chamadas do navegador mesmo com a API saudável. Manter também o polling do Vite já configurado para bind mounts. |
| Componentes React | Extrair telas/fluxos de [App.jsx](frontend/src/App.jsx) para componentes menores e isolar carregamento de dados e handlers. | Facilita testar estados de carregamento, erro, retry e submissão sem montar toda a aplicação em cada teste. |
| APIs do navegador | Encapsular `prompt`, `confirm`, `alert` e acesso ao `localStorage` atrás de funções/serviços substituíveis nos testes. | Evita diálogos bloqueantes e permite simular armazenamento e escolhas do usuário em testes de componente. |
| Configuração do frontend | Adicionar configuração e script de teste em [package.json do frontend](frontend/package.json), com ambiente DOM para Vitest/Testing Library. | Hoje o frontend não possui testes nem comando para executá-los; o script placeholder está somente no [pacote da raiz](package.json). |
| Ponta a ponta | Definir ambiente Playwright com API e frontend configurados para teste e dados isolados/resetáveis. | Permite reproduzir os fluxos de balcão sem depender do SQLite persistente de desenvolvimento ou produção. |

## Cobertura existente a considerar

Já há cobertura de API para CRUD e validação de produtos, aluguel/devolução, estoque, atraso/multa, planos, vendas, comprovantes e histórico em [test_api.py](backend/tests/test_api.py). Não foram encontrados testes de frontend. O plano acima complementa essa base e destaca lacunas, não exige implementar todas as camadas de uma vez.
