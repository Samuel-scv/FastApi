from datetime import date, timedelta


# ---------- helpers ----------
def novo_produto(client, **extra):
    corpo = {"titulo": "Filme", "preco_aluguel": 5, "preco_venda": 20, "estoque": 2, **extra}
    r = client.post("/produtos", json=corpo)
    assert r.status_code == 201, r.text
    return r.json()


def novo_cliente(client, **extra):
    r = client.post("/clientes", json={"nome": "Fulano", **extra})
    assert r.status_code == 201, r.text
    return r.json()


def novo_plano(client, **extra):
    r = client.post("/planos", json={"nome": "Gold", "preco_mensal": 30, "limite_mensal": 5, **extra})
    assert r.status_code == 201, r.text
    return r.json()


def alugar(client, cliente_id, produto_id, dias=3):
    return client.post("/alugueis", json={"cliente_id": cliente_id, "produto_id": produto_id, "dias": dias})


def estoque(client, produto_id):
    return client.get(f"/produtos/{produto_id}").json()["estoque"]


def atrasar(client, aluguel_id, dias):
    """Deixa o aluguel `dias` dias vencido, mexendo direto no banco de teste."""
    from app.core.database import get_db
    from app.main import app
    from app import models

    db = next(app.dependency_overrides[get_db]())
    a = db.get(models.Aluguel, aluguel_id)
    a.data_retirada = date.today() - timedelta(days=dias + 3)
    a.data_prevista = date.today() - timedelta(days=dias)
    db.commit()
    db.close()


# ---------- produtos ----------
def test_crud_de_produto(client):
    p = novo_produto(client, titulo="Bacurau")
    assert client.get("/produtos").json()[0]["titulo"] == "Bacurau"
    r = client.put(f"/produtos/{p['id']}", json={"estoque": 7})
    assert r.json()["estoque"] == 7 and r.json()["titulo"] == "Bacurau"
    assert client.delete(f"/produtos/{p['id']}").status_code == 204
    assert client.get(f"/produtos/{p['id']}").status_code == 404


def test_produto_invalido(client):
    assert client.post("/produtos", json={"titulo": "  "}).status_code == 422
    assert client.post("/produtos", json={"titulo": "X", "estoque": -1}).status_code == 422


# ---------- aluguel ----------
def test_aluguel_baixa_estoque_e_devolucao_repoe(client):
    p, c = novo_produto(client), novo_cliente(client)
    r = alugar(client, c["id"], p["id"])
    assert r.status_code == 201 and r.json()["status"] == "ativo"
    assert estoque(client, p["id"]) == 1
    r = client.post(f"/alugueis/{r.json()['id']}/devolucao", json={})
    assert r.status_code == 200 and r.json()["status"] == "devolvido" and r.json()["multa_paga"] == 0
    assert estoque(client, p["id"]) == 2


def test_sem_estoque_retorna_409(client):
    p, c = novo_produto(client, estoque=0), novo_cliente(client)
    assert alugar(client, c["id"], p["id"]).status_code == 409


def test_devolver_duas_vezes_retorna_409(client):
    p, c = novo_produto(client), novo_cliente(client)
    a = alugar(client, c["id"], p["id"]).json()
    assert client.post(f"/alugueis/{a['id']}/devolucao", json={}).status_code == 200
    assert client.post(f"/alugueis/{a['id']}/devolucao", json={}).status_code == 409
    assert estoque(client, p["id"]) == 2  # não repôs duas vezes


def test_atraso_gera_multa_e_bloqueia_cliente(client):
    p, p2, c = novo_produto(client), novo_produto(client, titulo="Outro"), novo_cliente(client)
    a = alugar(client, c["id"], p["id"]).json()
    atrasar(client, a["id"], dias=4)

    assert client.get(f"/clientes/{c['id']}").json()["bloqueado"] is True
    assert alugar(client, c["id"], p2["id"]).status_code == 409
    assert [x["id"] for x in client.get("/alugueis?status=atrasado").json()] == [a["id"]]

    r = client.post(f"/alugueis/{a['id']}/devolucao", json={})
    assert r.json()["dias_atraso"] == 4 and r.json()["multa_paga"] == 14.0  # 4 × R$ 3,50
    assert client.get(f"/clientes/{c['id']}").json()["bloqueado"] is False


def test_multa_pode_ser_sobrescrita_na_devolucao(client):
    p, c = novo_produto(client), novo_cliente(client)
    a = alugar(client, c["id"], p["id"]).json()
    atrasar(client, a["id"], dias=2)
    r = client.post(f"/alugueis/{a['id']}/devolucao", json={"multa": 0})
    assert r.json()["multa_paga"] == 0


def test_devolucao_nao_pode_ser_antes_da_retirada(client):
    p, c = novo_produto(client), novo_cliente(client)
    a = alugar(client, c["id"], p["id"]).json()
    ontem = (date.today() - timedelta(days=1)).isoformat()
    assert client.post(f"/alugueis/{a['id']}/devolucao", json={"data_devolucao": ontem}).status_code == 400


def test_filtro_de_status_invalido(client):
    assert client.get("/alugueis?status=banana").status_code == 422


def test_aluguel_em_lote_e_tudo_ou_nada(client):
    p1, p2 = novo_produto(client, titulo="A"), novo_produto(client, titulo="B", estoque=0)
    c = novo_cliente(client)

    r = client.post("/alugueis/lote", json={"cliente_id": c["id"], "produto_ids": [p1["id"], p2["id"]]})
    assert r.status_code == 409
    assert estoque(client, p1["id"]) == 2  # nada foi gravado
    assert client.get("/alugueis").json() == []

    p3 = novo_produto(client, titulo="C")
    r = client.post("/alugueis/lote", json={"cliente_id": c["id"], "produto_ids": [p1["id"], p3["id"]]})
    assert r.status_code == 201 and len(r.json()) == 2
    assert estoque(client, p1["id"]) == 1 and estoque(client, p3["id"]) == 1


def test_lote_com_titulo_repetido_respeita_estoque(client):
    p, c = novo_produto(client, estoque=1), novo_cliente(client)
    r = client.post("/alugueis/lote", json={"cliente_id": c["id"], "produto_ids": [p["id"], p["id"]]})
    assert r.status_code == 409
    assert estoque(client, p["id"]) == 1


# ---------- planos ----------
def test_plano_da_dias_extras_de_prazo(client):
    plano = novo_plano(client, dias_bonus=2)
    p, c = novo_produto(client), novo_cliente(client, plano_id=plano["id"])
    a = alugar(client, c["id"], p["id"], dias=3).json()
    prazo = date.fromisoformat(a["data_prevista"]) - date.fromisoformat(a["data_retirada"])
    assert prazo.days == 5


def test_carencia_de_multa_do_plano(client):
    plano = novo_plano(client, carencia_multa_dias=1)
    p, c = novo_produto(client), novo_cliente(client, plano_id=plano["id"])
    a = alugar(client, c["id"], p["id"]).json()
    atrasar(client, a["id"], dias=3)
    r = client.post(f"/alugueis/{a['id']}/devolucao", json={})
    assert r.json()["multa_paga"] == 7.0  # (3 − 1) × R$ 3,50


def test_assinar_plano_define_vencimento_e_cancelar_limpa(client):
    plano = novo_plano(client)
    c = novo_cliente(client)
    assert c["plano_status"] == "sem_plano" and c["plano_vencimento"] is None

    c = client.put(f"/clientes/{c['id']}", json={"plano_id": plano["id"]}).json()
    assert c["plano_status"] == "ativo"
    assert c["plano_vencimento"] == (date.today() + timedelta(days=30)).isoformat()
    assert c["limite_mensal"] == 5

    c = client.put(f"/clientes/{c['id']}", json={"plano_id": None}).json()
    assert c["plano_status"] == "sem_plano" and c["plano_vencimento"] is None


def test_plano_vencido_perde_beneficios_e_renovar_reativa(client):
    from app.core.database import get_db
    from app.main import app
    from app import models

    plano = novo_plano(client, dias_bonus=2)
    p, c = novo_produto(client), novo_cliente(client, plano_id=plano["id"])

    db = next(app.dependency_overrides[get_db]())
    db.get(models.Cliente, c["id"]).plano_vencimento = date.today() - timedelta(days=1)
    db.commit()
    db.close()

    c = client.get(f"/clientes/{c['id']}").json()
    assert c["plano_status"] == "vencido" and c["limite_mensal"] is None
    a = alugar(client, c["id"], p["id"], dias=3).json()
    assert (date.fromisoformat(a["data_prevista"]) - date.fromisoformat(a["data_retirada"])).days == 3  # sem bônus

    r = client.post(f"/clientes/{c['id']}/plano/renovar")
    assert r.status_code == 200 and r.json()["valor_cobrado"] == 30
    assert r.json()["novo_vencimento"] == (date.today() + timedelta(days=30)).isoformat()
    assert client.get(f"/clientes/{c['id']}").json()["plano_status"] == "ativo"


def test_renovar_em_dia_soma_a_partir_do_vencimento(client):
    plano = novo_plano(client)
    c = novo_cliente(client, plano_id=plano["id"])
    r = client.post(f"/clientes/{c['id']}/plano/renovar").json()
    assert r["novo_vencimento"] == (date.today() + timedelta(days=60)).isoformat()


def test_renovar_sem_plano_retorna_409(client):
    c = novo_cliente(client)
    assert client.post(f"/clientes/{c['id']}/plano/renovar").status_code == 409


def test_limite_mensal_avisa_mas_nao_bloqueia(client):
    plano = novo_plano(client, limite_mensal=1)
    p, c = novo_produto(client, estoque=3), novo_cliente(client, plano_id=plano["id"])
    assert alugar(client, c["id"], p["id"]).status_code == 201
    assert client.get(f"/clientes/{c['id']}").json()["limite_atingido"] is True
    assert alugar(client, c["id"], p["id"]).status_code == 201


def test_cliente_com_plano_inexistente(client):
    assert client.post("/clientes", json={"nome": "X", "plano_id": 999}).status_code == 400


def test_nao_exclui_plano_com_assinante(client):
    plano = novo_plano(client)
    novo_cliente(client, plano_id=plano["id"])
    assert client.delete(f"/planos/{plano['id']}").status_code == 409


# ---------- vendas ----------
def test_venda_baixa_estoque_e_gera_comprovante(client):
    p, c = novo_produto(client, titulo="Bacurau", preco_venda=44.9, estoque=3), novo_cliente(client, nome="Marina")
    r = client.post("/vendas", json={"cliente_id": c["id"], "produto_id": p["id"], "quantidade": 2})
    assert r.status_code == 201 and r.json()["valor_total"] == 89.8
    assert estoque(client, p["id"]) == 1

    comp = client.get(f"/vendas/{r.json()['id']}/comprovante").json()
    assert comp["cliente"] == "Marina" and comp["titulo"] == "Bacurau"
    assert comp["quantidade"] == 2 and comp["preco_unitario"] == 44.9


def test_venda_acima_do_estoque_retorna_409(client):
    p, c = novo_produto(client, estoque=1), novo_cliente(client)
    r = client.post("/vendas", json={"cliente_id": c["id"], "produto_id": p["id"], "quantidade": 2})
    assert r.status_code == 409
    assert estoque(client, p["id"]) == 1


def test_comprovante_de_venda_inexistente(client):
    assert client.get("/vendas/999/comprovante").status_code == 404


# ---------- integridade ----------
def test_nao_exclui_cliente_ou_produto_com_historico(client):
    p, c = novo_produto(client), novo_cliente(client)
    a = alugar(client, c["id"], p["id"]).json()
    assert client.delete(f"/clientes/{c['id']}").status_code == 409  # fita em aberto
    assert client.delete(f"/produtos/{p['id']}").status_code == 409

    client.post(f"/alugueis/{a['id']}/devolucao", json={})
    assert client.delete(f"/clientes/{c['id']}").status_code == 409  # tem histórico (antes dava 500)
    assert client.delete(f"/produtos/{p['id']}").status_code == 409


def test_historico_do_cliente(client):
    p, c = novo_produto(client, estoque=5), novo_cliente(client)
    alugar(client, c["id"], p["id"])
    client.post("/vendas", json={"cliente_id": c["id"], "produto_id": p["id"]})
    h = client.get(f"/clientes/{c['id']}/historico").json()
    assert h["cliente"]["id"] == c["id"] and len(h["alugueis"]) == 1 and len(h["vendas"]) == 1
    assert client.get("/clientes/999/historico").status_code == 404
