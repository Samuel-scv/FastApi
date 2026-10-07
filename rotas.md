# Rotas da API

Gerado a partir do `/openapi.json`. Documentação interativa em `/docs`.


## produtos

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/produtos` | Listar Produtos |
| POST | `/produtos` | Criar Produto |
| GET | `/produtos/{produto_id}` | Obter Produto |
| PUT | `/produtos/{produto_id}` | Atualizar Produto |
| DELETE | `/produtos/{produto_id}` | Excluir Produto |

## clientes

| Método | Rota | O que faz |
|--------|------|-----------|
| GET | `/clientes` | Listar Clientes |
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
