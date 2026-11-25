from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from app.core.seguranca import criar_token

USUARIO = {"nome": "Maria", "email": "Maria@Exemplo.com", "senha": "senha-forte-123"}


def registrar(c, **extra):
  return c.post("/auth/registrar", json={**USUARIO, **extra})


def login(c, email="maria@exemplo.com", senha=USUARIO["senha"]):
  return c.post("/auth/login", json={"email": email, "senha": senha})


def bearer(token):
  return {"Authorization": f"Bearer {token}"}


def test_registrar_cria_usuario_comum_e_nao_expoe_senha(anonimo):
  r = registrar(anonimo)
  assert r.status_code == 201
  corpo = r.json()
  assert corpo["email"] == "maria@exemplo.com" and corpo["admin"] is False and corpo["ativo"] is True
  assert "senha" not in corpo and "senha_hash" not in corpo


def test_registrar_nao_deixa_virar_admin_pelo_corpo(anonimo):
  assert registrar(anonimo, admin=True).json()["admin"] is False


def test_email_duplicado_e_senha_curta(anonimo):
  assert registrar(anonimo).status_code == 201
  assert registrar(anonimo).status_code == 409
  assert registrar(anonimo, email="b@b.com", senha="123").status_code == 422


def test_login_ok_e_erros(anonimo):
  registrar(anonimo)
  r = login(anonimo)
  assert r.status_code == 200 and r.json()["access_token"] and r.json()["refresh_token"]
  assert login(anonimo, senha="errada-errada").status_code == 401
  assert login(anonimo, email="ninguem@x.com").status_code == 401


def test_login_form_do_swagger(anonimo):
  registrar(anonimo)
  r = anonimo.post("/auth/login-form", data={"username": "maria@exemplo.com", "password": USUARIO["senha"]})
  assert r.status_code == 200 and r.json()["access_token"]


def test_me_com_e_sem_token(anonimo):
  registrar(anonimo)
  token = login(anonimo).json()["access_token"]
  assert anonimo.get("/auth/me").status_code == 401
  assert anonimo.get("/auth/me", headers=bearer(token)).json()["email"] == "maria@exemplo.com"
  assert anonimo.get("/auth/me", headers=bearer("lixo")).status_code == 401


def test_token_expirado_e_assinatura_falsa(anonimo):
  registrar(anonimo)
  payload = {"sub": "1", "tipo": "access", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)}
  expirado = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  falso = jwt.encode({**payload, "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, "outra-chave-qualquer-com-32-bytes!!", algorithm="HS256")
  assert anonimo.get("/auth/me", headers=bearer(expirado)).status_code == 401
  assert anonimo.get("/auth/me", headers=bearer(falso)).status_code == 401


def test_refresh_token_nao_serve_como_access_e_vice_versa(anonimo):
  registrar(anonimo)
  tokens = login(anonimo).json()
  assert anonimo.get("/auth/me", headers=bearer(tokens["refresh_token"])).status_code == 401
  assert anonimo.post("/auth/refresh", json={"refresh_token": tokens["access_token"]}).status_code == 401
  r = anonimo.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
  assert r.status_code == 200
  assert anonimo.get("/auth/me", headers=bearer(r.json()["access_token"])).status_code == 200


def test_rotas_protegidas_exigem_login(anonimo):
  for caminho in ["/clientes", "/alugueis", "/vendas"]:
    assert anonimo.get(caminho).status_code == 401, caminho


def test_catalogo_e_publico_para_leitura(anonimo):
  assert anonimo.get("/produtos").status_code == 200
  assert anonimo.get("/planos").status_code == 200
  assert anonimo.get("/health").status_code == 200


def test_escrita_do_catalogo_so_admin(anonimo):
  corpo = {"titulo": "Filme", "preco_aluguel": 5, "preco_venda": 20, "estoque": 1}
  assert anonimo.post("/produtos", json=corpo).status_code == 401
  registrar(anonimo)
  token = login(anonimo).json()["access_token"]
  assert anonimo.post("/produtos", json=corpo, headers=bearer(token)).status_code == 403
  assert anonimo.get("/clientes", headers=bearer(token)).status_code == 403  # cliente cadastrado no site não vê dados da loja


def test_admin_escreve_no_catalogo(client):
  corpo = {"titulo": "Filme", "preco_aluguel": 5, "preco_venda": 20, "estoque": 1}
  assert client.post("/produtos", json=corpo).status_code == 201


def test_usuario_inativo_perde_acesso(client, anonimo):
  from app import models
  from app.core.database import get_db
  from app.main import app

  registrar(anonimo)
  token = login(anonimo).json()["access_token"]
  db = next(app.dependency_overrides[get_db]())
  db.query(models.Usuario).filter_by(email="maria@exemplo.com").one().ativo = False
  db.commit()
  assert anonimo.get("/auth/me", headers=bearer(token)).status_code == 401
  assert login(anonimo).status_code == 401
  assert criar_token(1)  # sanity: gerar token continua funcionando
