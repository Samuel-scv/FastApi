# Rotas da API

Gerado a partir do `/openapi.json`. Documentação interativa em `/docs`.


## produtos

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/produtos` | Listar produtos (paginado; filtros `q`, `genero`, `diretor`, `tipo`, `disponivel`; `ordenar_por=nota` para os mais bem avaliados) |
| POST | `/produtos` | Criar Produto |
| GET | `/produtos/{produto_id}` | Obter Produto |
| PUT | `/produtos/{produto_id}` | Atualizar Produto |
| DELETE | `/produtos/{produto_id}` | Excluir Produto |

## perguntas

Cliente logado pergunta, vendedor responde. Só as respondidas aparecem na vitrine do título.

| Método | Rota | Quem | O que faz |
|--------|------|------|-----------|
| GET | `/perguntas/produto/{produto_id}` | público | Perguntas respondidas do título |
| POST | `/perguntas/produto/{produto_id}` | logado | Fazer uma pergunta (máx. 5 pendentes por pessoa) |
| GET | `/perguntas/minhas` | logado | Minhas perguntas, com ou sem resposta |
| GET | `/perguntas` | vendedor | Caixa de entrada. `status=pendente` é a fila para responder |
| POST | `/perguntas/{pergunta_id}/resposta` | vendedor | Responder (uma vez por pergunta) |
| DELETE | `/perguntas/{pergunta_id}` | autor ou vendedor | Autor só apaga enquanto não respondida; vendedor modera |

## avaliacoes

Cliente avalia um título que já alugou ou comprou (exige que o cadastro de balcão esteja vinculado à conta do site).

| Método | Rota | Quem | O que faz |
|--------|------|------|-----------|
| GET | `/avaliacoes/produto/{produto_id}` | público, paginado | Avaliações do título |
| POST | `/avaliacoes/produto/{produto_id}` | logado | Avaliar (nota 1–5 + comentário), uma vez por título |

## favoritos

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/favoritos` | Meus favoritos |
| POST | `/favoritos/{produto_id}` | Adicionar |
| DELETE | `/favoritos/{produto_id}` | Remover |

## reservas

Fila de espera para título zerado (`produto.estoque == 0`). Vendedor.

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/reservas` | Lista, com `status` e `produto_id`. `status=disponivel` é quem já pode ser avisado |
| POST | `/reservas` | Entra na fila |
| POST | `/reservas/{id}/atender` | Confirma retirada: abre o aluguel e fecha a reserva |
| DELETE | `/reservas/{id}` | Cancela |

Toda entrada ou devolução de estoque promove automaticamente quem está há mais tempo na fila.

## relatorios

Vendedor.

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/relatorios/faturamento` | Total por aluguel/venda/multa no período (padrão: mês atual), com série por dia e ticket médio |
| GET | `/relatorios/mais-alugados` | Ranking por quantidade de aluguéis |
| GET | `/relatorios/mais-vendidos` | Ranking por quantidade vendida |
| GET | `/relatorios/dashboard` | Resumo para a tela inicial do balcão |

## usuarios

Só admin. Quem se cadastra em `/auth/registrar` entra como cliente; aqui se promove a vendedor.

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/usuarios` | Listar usuários |
| PATCH | `/usuarios/{usuario_id}` | Definir `vendedor`, `admin` ou `ativo` |

## estoque

Exigem login. `perda` e `ajuste` só para admin.

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/estoque` | Posição por título (disponível, alugadas, total, situação). Filtros: `tipo=filme\|serie`, `situacao=ok\|baixo\|zerado` |
| GET | `/estoque/movimentos` | Histórico de movimentações, paginado. Filtros: `produto_id`, `tipo` |
| POST | `/estoque/{produto_id}/entrada` | Chegada de cópias (compra, doação) |
| POST | `/estoque/{produto_id}/perda` | Baixa de cópia danificada ou extraviada (admin) |
| POST | `/estoque/{produto_id}/ajuste` | Inventário: informa a contagem real e registra a diferença (admin) |

## clientes

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/clientes` | Listar clientes (paginado; filtro `q` por nome) |
| POST | `/clientes` | Criar Cliente |
| GET | `/clientes/{cliente_id}` | Obter Cliente |
| PUT | `/clientes/{cliente_id}` | Atualizar Cliente |
| DELETE | `/clientes/{cliente_id}` | Excluir Cliente |
| GET | `/clientes/{cliente_id}/historico` | Historico Do Cliente |
| POST | `/clientes/{cliente_id}/plano/renovar` | Renovar Plano |

## planos

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/planos` | Listar Planos |
| POST | `/planos` | Criar Plano |
| GET | `/planos/{plano_id}` | Obter Plano |
| PUT | `/planos/{plano_id}` | Atualizar Plano |
| DELETE | `/planos/{plano_id}` | Excluir Plano |

## alugueis

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/alugueis` | Listar Alugueis |
| POST | `/alugueis` | Registrar Aluguel |
| POST | `/alugueis/lote` | Registrar Aluguel Em Lote |
| GET | `/alugueis/{aluguel_id}` | Obter Aluguel |
| POST | `/alugueis/{aluguel_id}/devolucao` | Devolver Aluguel |

## vendas

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/vendas` | Listar Vendas |
| POST | `/vendas` | Registrar Venda |
| GET | `/vendas/{venda_id}` | Obter Venda |
| GET | `/vendas/{venda_id}/comprovante` | Comprovante Da Venda |

## status

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/` | Raiz |
