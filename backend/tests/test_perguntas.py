from tests.test_api import novo_produto
from tests.test_auth import bearer


def cadastrar(c, nome, email):
  c.post("/auth/registrar", json={"nome": nome, "email": email, "senha": "senha-forte-123"})
  token = c.post("/auth/login", json={"email": email, "senha": "senha-forte-123"}).json()["access_token"]
  return bearer(token), c.get("/auth/me", headers=bearer(token)).json()["id"]


def cliente_e_vendedor(client, anonimo):
  cli, _ = cadastrar(anonimo, "Maria Souza", "maria@x.com")
  ven, vid = cadastrar(anonimo, "João Vendedor", "joao@x.com")
  assert client.patch(f"/usuarios/{vid}", json={"vendedor": True}).status_code == 200
  return cli, ven


def test_fluxo_completo_pergunta_e_resposta(client, anonimo):
  p = novo_produto(client, titulo="Bacurau")
  cli, ven = cliente_e_vendedor(client, anonimo)

  r = anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Tem a versão dublada?"}, headers=cli)
  assert r.status_code == 201
  q = r.json()
  assert q["status"] == "pendente" and q["autor"] == "Maria" and q["titulo"] == "Bacurau" and q["resposta"] is None

  assert anonimo.get(f"/perguntas/produto/{p['id']}").json() == []  # pendente não aparece na vitrine
  assert [x["id"] for x in anonimo.get("/perguntas", params={"status": "pendente"}, headers=ven).json()] == [q["id"]]

  r = anonimo.post(f"/perguntas/{q['id']}/resposta", json={"texto": "Tem sim, dublada e legendada."}, headers=ven)
  assert r.status_code == 200 and r.json()["status"] == "respondida" and r.json()["vendedor"] == "João"

  publica = anonimo.get(f"/perguntas/produto/{p['id']}").json()  # agora aparece, sem login
  assert len(publica) == 1 and publica[0]["resposta"] == "Tem sim, dublada e legendada."
  assert anonimo.get("/perguntas/minhas", headers=cli).json()[0]["status"] == "respondida"
  assert anonimo.get("/perguntas", params={"status": "pendente"}, headers=ven).json() == []


def test_so_responde_uma_vez(client, anonimo):
  p = novo_produto(client)
  cli, ven = cliente_e_vendedor(client, anonimo)
  q = anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Está disponível?"}, headers=cli).json()
  assert anonimo.post(f"/perguntas/{q['id']}/resposta", json={"texto": "Sim"}, headers=ven).status_code == 200
  assert anonimo.post(f"/perguntas/{q['id']}/resposta", json={"texto": "De novo"}, headers=ven).status_code == 409


def test_permissoes(client, anonimo):
  p = novo_produto(client)
  cli, ven = cliente_e_vendedor(client, anonimo)
  assert anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Alguém aí?"}).status_code == 401
  q = anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Tem em Blu-ray?"}, headers=cli).json()
  assert anonimo.get("/perguntas", headers=cli).status_code == 403  # cliente não vê a caixa dos vendedores
  assert anonimo.post(f"/perguntas/{q['id']}/resposta", json={"texto": "eu mesmo respondo"}, headers=cli).status_code == 403
  outro, _ = cadastrar(anonimo, "Pedro", "pedro@x.com")
  assert anonimo.delete(f"/perguntas/{q['id']}", headers=outro).status_code == 403
  assert anonimo.get("/perguntas/minhas", headers=outro).json() == []


def test_validacoes_e_titulo_inexistente(client, anonimo):
  p = novo_produto(client)
  cli, _ = cliente_e_vendedor(client, anonimo)
  assert anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "oi"}, headers=cli).status_code == 422
  assert anonimo.post("/perguntas/produto/999", json={"texto": "Existe esse filme?"}, headers=cli).status_code == 404
  assert anonimo.get("/perguntas/produto/999").status_code == 404


def test_limite_de_pendentes(client, anonimo):
  p = novo_produto(client)
  cli, _ = cliente_e_vendedor(client, anonimo)
  for i in range(5):
    assert anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": f"Pergunta número {i}"}, headers=cli).status_code == 201
  assert anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Mais uma pergunta"}, headers=cli).status_code == 409


def test_apagar_pergunta(client, anonimo):
  p = novo_produto(client)
  cli, ven = cliente_e_vendedor(client, anonimo)
  q1 = anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Pergunta que vou apagar"}, headers=cli).json()
  assert anonimo.delete(f"/perguntas/{q1['id']}", headers=cli).status_code == 204  # autor, ainda sem resposta
  q2 = anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Pergunta que será respondida"}, headers=cli).json()
  anonimo.post(f"/perguntas/{q2['id']}/resposta", json={"texto": "ok"}, headers=ven)
  assert anonimo.delete(f"/perguntas/{q2['id']}", headers=cli).status_code == 403  # respondida: autor não apaga
  assert anonimo.delete(f"/perguntas/{q2['id']}", headers=ven).status_code == 204  # vendedor modera
  assert anonimo.delete(f"/perguntas/{q2['id']}", headers=ven).status_code == 404


def test_admin_gerencia_usuarios(client, anonimo):
  cli, _ = cadastrar(anonimo, "Maria", "maria@x.com")
  assert anonimo.get("/usuarios", headers=cli).status_code == 403
  usuarios = client.get("/usuarios").json()
  assert {u["email"] for u in usuarios} == {"admin@teste.com", "maria@x.com"}
  assert all(u["vendedor"] is False for u in usuarios if u["email"] == "maria@x.com")
  eu = next(u for u in usuarios if u["email"] == "admin@teste.com")
  assert client.patch(f"/usuarios/{eu['id']}", json={"admin": False}).status_code == 409  # não se rebaixa
  assert client.patch(f"/usuarios/{eu['id']}", json={"ativo": False}).status_code == 409
  assert client.patch("/usuarios/999", json={"vendedor": True}).status_code == 404
  maria = next(u for u in usuarios if u["email"] == "maria@x.com")
  assert client.patch(f"/usuarios/{maria['id']}", json={"ativo": False}).json()["ativo"] is False
  assert anonimo.get("/auth/me", headers=cli).status_code == 401  # conta desativada perde o acesso


def test_excluir_titulo_leva_historico_junto(client, anonimo):
  p = novo_produto(client, estoque=2)
  cli, _ = cliente_e_vendedor(client, anonimo)
  anonimo.post(f"/perguntas/produto/{p['id']}", json={"texto": "Esse título some?"}, headers=cli)
  assert client.delete(f"/produtos/{p['id']}").status_code == 204
  assert client.get("/estoque/movimentos").status_code == 200 and client.get("/estoque/movimentos").json()["itens"] == []
  assert anonimo.get("/perguntas/minhas", headers=cli).json() == []
