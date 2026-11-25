"""Paginação, busca, avaliações, favoritos, reservas e relatórios."""
from datetime import date, timedelta

from tests.test_api import alugar, atrasar, estoque, novo_cliente, novo_plano, novo_produto
from tests.test_auth import bearer
from tests.test_perguntas import cadastrar


def cliente_logado(client, anonimo, cliente_id=None, nome="Maria Souza", email="maria@x.com"):
  """Cadastra uma conta de site e, se vier `cliente_id`, vincula ao cadastro de balcão."""
  token, uid = cadastrar(anonimo, nome, email)
  if cliente_id is not None:
    assert client.post(f"/clientes/{cliente_id}/vincular-usuario", json={"usuario_id": uid}).status_code == 200
  return token, uid


# ---------- paginação ----------
def test_paginacao_de_produtos(client):
  for i in range(25):
    novo_produto(client, titulo=f"Filme {i:02d}")
  p1 = client.get("/produtos", params={"pagina": 1, "por_pagina": 10}).json()
  assert len(p1["itens"]) == 10 and p1["total"] == 25 and p1["paginas"] == 3
  p3 = client.get("/produtos", params={"pagina": 3, "por_pagina": 10}).json()
  assert len(p3["itens"]) == 5
  assert client.get("/produtos", params={"pagina": 1, "por_pagina": 500}).status_code == 422


def test_paginacao_de_clientes_e_busca_por_nome(client):
  novo_cliente(client, nome="Ana Paula")
  novo_cliente(client, nome="Ana Beatriz")
  novo_cliente(client, nome="Bruno")
  r = client.get("/clientes", params={"q": "ana"}).json()
  assert r["total"] == 2 and all("ana" in c["nome"].lower() for c in r["itens"])


# ---------- busca e filtro no catálogo ----------
def test_busca_e_filtros_do_catalogo(client):
  novo_produto(client, titulo="Bacurau", genero="Drama", diretor="Kleber Mendonça", estoque=1)
  novo_produto(client, titulo="3%", tipo="serie", genero="Ficção", estoque=0)
  r = client.get("/produtos", params={"q": "bacu"}).json()
  assert [p["titulo"] for p in r["itens"]] == ["Bacurau"]
  assert client.get("/produtos", params={"genero": "ficção"}).json()["total"] == 1
  assert client.get("/produtos", params={"tipo": "serie"}).json()["total"] == 1
  assert client.get("/produtos", params={"disponivel": True}).json()["total"] == 1
  assert client.get("/produtos", params={"disponivel": False}).json()["total"] == 1


def test_ordenar_por_nota(client, anonimo):
  ruim = novo_produto(client, titulo="Ruim", estoque=2)
  bom = novo_produto(client, titulo="Bom", estoque=2)
  c = novo_cliente(client)
  alugar(client, c["id"], ruim["id"]); alugar(client, c["id"], bom["id"])
  token, _ = cliente_logado(client, anonimo, c["id"])
  anonimo.post(f"/avaliacoes/produto/{ruim['id']}", json={"nota": 1}, headers=token)
  anonimo.post(f"/avaliacoes/produto/{bom['id']}", json={"nota": 5}, headers=token)
  r = client.get("/produtos", params={"ordenar_por": "nota"}).json()["itens"]
  assert [p["titulo"] for p in r[:2]] == ["Bom", "Ruim"]
  assert r[0]["nota_media"] == 5.0 and r[0]["total_avaliacoes"] == 1


# ---------- avaliações ----------
def test_avaliar_exige_vinculo_e_consumo_previo(client, anonimo):
  p = novo_produto(client, estoque=1)
  c = novo_cliente(client)
  token, uid = cadastrar(anonimo, "Maria Souza", "maria@x.com")

  r = anonimo.post(f"/avaliacoes/produto/{p['id']}", json={"nota": 5}, headers=token)
  assert r.status_code == 409  # ainda não vinculada a um cliente

  client.post(f"/clientes/{c['id']}/vincular-usuario", json={"usuario_id": uid})
  r = anonimo.post(f"/avaliacoes/produto/{p['id']}", json={"nota": 5}, headers=token)
  assert r.status_code == 403  # vinculada, mas nunca alugou/comprou esse título

  alugar(client, c["id"], p["id"])
  r = anonimo.post(f"/avaliacoes/produto/{p['id']}", json={"nota": 4, "comentario": "Bom filme"}, headers=token)
  assert r.status_code == 201 and r.json()["cliente"] == "Fulano"  # nome vem do cadastro de balcão (novo_cliente), não do login
  assert anonimo.post(f"/avaliacoes/produto/{p['id']}", json={"nota": 3}, headers=token).status_code == 409  # já avaliou
  assert anonimo.post(f"/avaliacoes/produto/999", json={"nota": 3}, headers=token).status_code == 404
  assert anonimo.post(f"/avaliacoes/produto/{p['id']}", json={"nota": 6}).status_code in (401, 422)
  publicas = anonimo.get(f"/avaliacoes/produto/{p['id']}").json()
  assert publicas["total"] == 1 and publicas["itens"][0]["comentario"] == "Bom filme"


def test_vincular_usuario_nao_duplica(client, anonimo):
  c1, c2 = novo_cliente(client, nome="A"), novo_cliente(client, nome="B")
  _, uid = cadastrar(anonimo, "Maria", "maria@x.com")
  assert client.post(f"/clientes/{c1['id']}/vincular-usuario", json={"usuario_id": uid}).status_code == 200
  assert client.post(f"/clientes/{c2['id']}/vincular-usuario", json={"usuario_id": uid}).status_code == 409
  assert client.post(f"/clientes/{c1['id']}/vincular-usuario", json={"usuario_id": 999}).status_code == 404


# ---------- favoritos ----------
def test_favoritos(client, anonimo):
  p1, p2 = novo_produto(client, titulo="A"), novo_produto(client, titulo="B")
  token, _ = cadastrar(anonimo, "Maria", "maria@x.com")
  assert anonimo.post(f"/favoritos/{p1['id']}", headers=token).status_code == 201
  assert anonimo.post(f"/favoritos/{p1['id']}", headers=token).status_code == 409
  assert anonimo.post("/favoritos/999", headers=token).status_code == 404
  anonimo.post(f"/favoritos/{p2['id']}", headers=token)
  titulos = {f["titulo"] for f in anonimo.get("/favoritos", headers=token).json()}
  assert titulos == {"A", "B"}
  assert anonimo.delete(f"/favoritos/{p1['id']}", headers=token).status_code == 204
  assert anonimo.delete(f"/favoritos/{p1['id']}", headers=token).status_code == 404
  assert len(anonimo.get("/favoritos", headers=token).json()) == 1
  assert anonimo.get("/favoritos").status_code == 401


# ---------- reservas ----------
def test_reserva_so_para_titulo_zerado_e_ordem_fifo(client):
  cheio = novo_produto(client, titulo="Cheio", estoque=1)
  zerado = novo_produto(client, titulo="Zerado", estoque=0)
  c1, c2 = novo_cliente(client, nome="Ana"), novo_cliente(client, nome="Beto")

  r = client.post("/reservas", json={"cliente_id": c1["id"], "produto_id": cheio["id"]})
  assert r.status_code == 409

  r1 = client.post("/reservas", json={"cliente_id": c1["id"], "produto_id": zerado["id"]})
  assert r1.status_code == 201 and r1.json()["status"] == "aguardando" and r1.json()["posicao_na_fila"] == 1
  r2 = client.post("/reservas", json={"cliente_id": c2["id"], "produto_id": zerado["id"]})
  assert r2.json()["posicao_na_fila"] == 2
  assert client.post("/reservas", json={"cliente_id": c1["id"], "produto_id": zerado["id"]}).status_code == 409  # já está na fila


def test_entrada_promove_o_mais_antigo_da_fila(client):
  p = novo_produto(client, estoque=0)
  c1, c2 = novo_cliente(client, nome="Ana"), novo_cliente(client, nome="Beto")
  r1 = client.post("/reservas", json={"cliente_id": c1["id"], "produto_id": p["id"]}).json()
  r2 = client.post("/reservas", json={"cliente_id": c2["id"], "produto_id": p["id"]}).json()

  client.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 1, "motivo": "comprou mais uma"})
  fila = client.get("/reservas", params={"produto_id": p["id"]}).json()
  por_id = {x["id"]: x for x in fila}
  assert por_id[r1["id"]]["status"] == "disponivel" and por_id[r2["id"]]["status"] == "aguardando" and por_id[r2["id"]]["posicao_na_fila"] == 1

  client.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 1})
  assert client.get("/reservas", params={"produto_id": p["id"]}).json()[1]["status"] == "disponivel"


def test_devolucao_tambem_promove_a_fila(client):
  p = novo_produto(client, estoque=1)
  dono = novo_cliente(client, nome="Dono")
  a = alugar(client, dono["id"], p["id"]).json()
  esperando = novo_cliente(client, nome="Esperando")
  reserva = client.post("/reservas", json={"cliente_id": esperando["id"], "produto_id": p["id"]}).json()
  client.post(f"/alugueis/{a['id']}/devolucao", json={})
  assert client.get(f"/reservas/{reserva['id']}".replace(f"/reservas/{reserva['id']}", "/reservas"), params={"produto_id": p["id"]}).json()[0]["status"] == "disponivel"


def test_atender_reserva_abre_aluguel_e_fecha_a_reserva(client):
  p = novo_produto(client, estoque=0)
  c = novo_cliente(client)
  reserva = client.post("/reservas", json={"cliente_id": c["id"], "produto_id": p["id"]}).json()
  assert client.post(f"/reservas/{reserva['id']}/atender", json={}).status_code == 409  # ainda aguardando

  client.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 1})
  r = client.post(f"/reservas/{reserva['id']}/atender", json={"dias": 5})
  assert r.status_code == 200 and r.json()["status"] == "ativo" and r.json()["cliente_id"] == c["id"]
  assert client.get("/reservas", params={"produto_id": p["id"]}).json()[0]["status"] == "atendida"
  assert estoque(client, p["id"]) == 0


def test_cancelar_reserva_disponivel_repassa_a_vaga(client):
  p = novo_produto(client, estoque=0)
  c1, c2 = novo_cliente(client, nome="Ana"), novo_cliente(client, nome="Beto")
  r1 = client.post("/reservas", json={"cliente_id": c1["id"], "produto_id": p["id"]}).json()
  r2 = client.post("/reservas", json={"cliente_id": c2["id"], "produto_id": p["id"]}).json()
  client.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 1})  # promove r1

  assert client.delete(f"/reservas/{r1['id']}").status_code == 204
  fila = {x["id"]: x for x in client.get("/reservas", params={"produto_id": p['id']}).json()}
  assert fila[r1["id"]]["status"] == "cancelada" and fila[r2["id"]]["status"] == "disponivel"
  assert client.delete(f"/reservas/{r1['id']}").status_code == 409


def test_permissoes_de_reserva(client, anonimo):
  p = novo_produto(client, estoque=0)
  c = novo_cliente(client)
  token, _ = cadastrar(anonimo, "Maria", "maria@x.com")
  assert anonimo.post("/reservas", json={"cliente_id": c["id"], "produto_id": p["id"]}, headers=token).status_code == 403


# ---------- relatórios ----------
def test_faturamento_soma_aluguel_venda_e_multa(client):
  p = novo_produto(client, preco_aluguel=10, preco_venda=50, estoque=5)
  c = novo_cliente(client)
  a = alugar(client, c["id"], p["id"]).json()
  atrasar(client, a["id"], dias=2)
  client.post(f"/alugueis/{a['id']}/devolucao", json={})
  client.post("/vendas", json={"cliente_id": c["id"], "produto_id": p["id"], "quantidade": 1})

  r = client.get("/relatorios/faturamento").json()
  assert r["total_aluguel"] == 10 and r["total_venda"] == 50 and r["total_multa"] == 7.0
  assert r["total_geral"] == 67.0 and r["quantidade_alugueis"] == 1 and r["quantidade_vendas"] == 1
  assert r["ticket_medio"] == 33.5
  assert sum(ponto["total"] for ponto in r["por_dia"]) == 67.0

  ontem = (date.today() - timedelta(days=1)).isoformat()
  vazio = client.get("/relatorios/faturamento", params={"inicio": ontem, "fim": ontem}).json()
  assert vazio["total_geral"] == 0 and vazio["por_dia"] == []
  assert client.get("/relatorios/faturamento", params={"inicio": date.today().isoformat(), "fim": ontem}).status_code == 400


def test_mais_alugados_e_mais_vendidos(client):
  mais = novo_produto(client, titulo="Mais alugado", estoque=5)
  menos = novo_produto(client, titulo="Menos alugado", estoque=5)
  c = novo_cliente(client)
  alugar(client, c["id"], mais["id"]); alugar(client, c["id"], mais["id"]); alugar(client, c["id"], menos["id"])
  client.post("/vendas", json={"cliente_id": c["id"], "produto_id": mais["id"], "quantidade": 3})

  ranking = client.get("/relatorios/mais-alugados", params={"limite": 1}).json()
  assert len(ranking) == 1 and ranking[0]["titulo"] == "Mais alugado" and ranking[0]["quantidade"] == 2
  vendidos = client.get("/relatorios/mais-vendidos").json()
  assert vendidos[0]["titulo"] == "Mais alugado" and vendidos[0]["quantidade"] == 3


def test_dashboard_agrega_indicadores(client):
  p = novo_produto(client, estoque=1, estoque_minimo=5)
  c = novo_cliente(client)
  a = alugar(client, c["id"], p["id"]).json()
  atrasar(client, a["id"], dias=1)

  d = client.get("/relatorios/dashboard").json()
  assert d["alugueis_ativos"] == 1 and d["alugueis_atrasados"] == 1 and d["clientes_bloqueados"] == 1
  assert d["titulos_estoque_baixo"] == 1 and d["titulos_estoque_zerado"] == 0


def test_relatorios_exigem_vendedor(anonimo):
  assert anonimo.get("/relatorios/dashboard").status_code == 401
