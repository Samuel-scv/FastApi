from tests.test_api import alugar, estoque, novo_cliente, novo_produto

from tests.test_auth import USUARIO, bearer, registrar


def movimentos(client, produto_id, **filtros):
  return client.get("/estoque/movimentos", params={"produto_id": produto_id, "por_pagina": 100, **filtros}).json()["itens"]


def test_cadastro_com_estoque_gera_movimento_inicial(client):
  p = novo_produto(client, estoque=3)
  [m] = movimentos(client, p["id"])
  assert m["tipo"] == "inicial" and m["quantidade"] == 3 and m["saldo_apos"] == 3


def test_filme_e_serie(client):
  filme = novo_produto(client, titulo="Bacurau")
  serie = novo_produto(client, titulo="3%", tipo="serie", temporadas=4)
  assert filme["tipo"] == "filme" and filme["temporadas"] is None
  assert serie["tipo"] == "serie" and serie["temporadas"] == 4
  assert client.post("/produtos", json={"titulo": "X", "tipo": "documentario"}).status_code == 422
  tipos = {i["tipo"] for i in client.get("/estoque", params={"tipo": "serie"}).json()["itens"]}
  assert tipos == {"serie"}


def test_entrada_soma_e_registra_usuario(client):
  p = novo_produto(client, estoque=1)
  r = client.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 4, "motivo": "compra do fornecedor"})
  assert r.status_code == 201
  assert r.json()["saldo_apos"] == 5 and r.json()["usuario_id"] is not None and r.json()["titulo"] == "Filme"
  assert estoque(client, p["id"]) == 5
  assert client.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 0}).status_code == 422


def test_aluguel_devolucao_e_venda_entram_no_historico(client):
  p = novo_produto(client, estoque=3)
  c = novo_cliente(client)
  aluguel = alugar(client, c["id"], p["id"]).json()
  client.post(f"/alugueis/{aluguel['id']}/devolucao", json={})
  client.post("/vendas", json={"cliente_id": c["id"], "produto_id": p["id"], "quantidade": 2})
  tipos = [(m["tipo"], m["quantidade"], m["saldo_apos"]) for m in reversed(movimentos(client, p["id"]))]
  assert tipos == [("inicial", 3, 3), ("aluguel", -1, 2), ("devolucao", 1, 3), ("venda", -2, 1)]
  assert estoque(client, p["id"]) == 1
  m_aluguel = movimentos(client, p["id"], tipo="aluguel")[0]
  assert m_aluguel["aluguel_id"] == aluguel["id"]


def test_perda_baixa_e_nao_passa_do_saldo(client):
  p = novo_produto(client, estoque=2)
  assert client.post(f"/estoque/{p['id']}/perda", json={"quantidade": 1, "motivo": "disco riscado"}).status_code == 201
  assert estoque(client, p["id"]) == 1
  assert client.post(f"/estoque/{p['id']}/perda", json={"quantidade": 5, "motivo": "extravio"}).status_code == 409
  assert client.post(f"/estoque/{p['id']}/perda", json={"quantidade": 1}).status_code == 422  # motivo é obrigatório
  assert estoque(client, p["id"]) == 1


def test_ajuste_de_inventario(client):
  p = novo_produto(client, estoque=5)
  r = client.post(f"/estoque/{p['id']}/ajuste", json={"saldo": 3, "motivo": "inventário"})
  assert r.status_code == 201 and r.json()["quantidade"] == -2 and r.json()["saldo_apos"] == 3
  assert estoque(client, p["id"]) == 3
  assert client.post(f"/estoque/{p['id']}/ajuste", json={"saldo": 3, "motivo": "de novo"}).status_code == 400


def test_editar_estoque_pelo_cadastro_vira_ajuste(client):
  p = novo_produto(client, estoque=2)
  assert client.put(f"/produtos/{p['id']}", json={"estoque": 7}).json()["estoque"] == 7
  ultimo = movimentos(client, p["id"])[0]
  assert ultimo["tipo"] == "ajuste" and ultimo["quantidade"] == 5 and ultimo["saldo_apos"] == 7
  client.put(f"/produtos/{p['id']}", json={"titulo": "Outro nome"})  # sem mexer no estoque: sem movimento novo
  assert len(movimentos(client, p["id"])) == 2


def test_resumo_alugadas_total_e_situacao(client):
  p = novo_produto(client, titulo="A", estoque=2, estoque_minimo=2)  # total 2 <= minimo 2 -> baixo
  ok = novo_produto(client, titulo="B", estoque=10)
  zero = novo_produto(client, titulo="C", estoque=0)
  c = novo_cliente(client)
  alugar(client, c["id"], p["id"])
  resumo = client.get("/estoque").json()
  por_id = {i["produto_id"]: i for i in resumo["itens"]}
  assert (por_id[p["id"]]["disponivel"], por_id[p["id"]]["alugadas"], por_id[p["id"]]["total_acervo"]) == (1, 1, 2)
  assert por_id[p["id"]]["situacao"] == "baixo" and por_id[ok["id"]]["situacao"] == "ok" and por_id[zero["id"]]["situacao"] == "zerado"
  assert resumo["titulos_baixos"] == 1 and resumo["titulos_zerados"] == 1 and resumo["copias_alugadas"] == 1
  baixos = client.get("/estoque", params={"situacao": "baixo"}).json()["itens"]
  assert [i["titulo"] for i in baixos] == ["A"]


def test_todas_alugadas_nao_e_estoque_zerado(client):
  p = novo_produto(client, estoque=1)
  c = novo_cliente(client)
  alugar(client, c["id"], p["id"])
  item = client.get("/estoque").json()["itens"][0]
  assert item["disponivel"] == 0 and item["total_acervo"] == 1 and item["todas_alugadas"] is True and item["situacao"] != "zerado"


def test_permissoes(client, anonimo):
  p = novo_produto(client, estoque=2)
  assert anonimo.get("/estoque").status_code == 401
  registrar(anonimo)
  token = anonimo.post("/auth/login", json={"email": "maria@exemplo.com", "senha": USUARIO["senha"]}).json()["access_token"]
  h = bearer(token)
  assert anonimo.get("/estoque", headers=h).status_code == 403  # cliente comum não acessa o estoque
  assert anonimo.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 1}, headers=h).status_code == 403
  uid = anonimo.get("/auth/me", headers=h).json()["id"]
  assert client.patch(f"/usuarios/{uid}", json={"vendedor": True}).status_code == 200
  assert anonimo.get("/estoque", headers=h).status_code == 200
  assert anonimo.post(f"/estoque/{p['id']}/entrada", json={"quantidade": 1}, headers=h).status_code == 201
  assert anonimo.post(f"/estoque/{p['id']}/perda", json={"quantidade": 1, "motivo": "x"}, headers=h).status_code == 403
  assert anonimo.post(f"/estoque/{p['id']}/ajuste", json={"saldo": 0, "motivo": "x"}, headers=h).status_code == 403


def test_sincronizar_saldos_de_banco_antigo(client):
  from app import models
  from app.core.database import get_db
  from app.main import app
  from app.services.estoque import sincronizar_saldos_iniciais

  db = next(app.dependency_overrides[get_db]())
  antigo = models.Produto(titulo="Legado", estoque=4)  # criado direto, sem histórico
  db.add(antigo)
  db.commit()
  sincronizar_saldos_iniciais(db)
  sincronizar_saldos_iniciais(db)  # idempotente
  [m] = movimentos(client, antigo.id)
  assert m["tipo"] == "inicial" and m["saldo_apos"] == 4
