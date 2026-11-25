from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.core.database import Base
from app.services import usuarios as service


def _db():
  engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
  Base.metadata.create_all(bind=engine)
  return sessionmaker(bind=engine)()


def test_vendedor_inicial_e_criado_so_com_vendedor_e_sem_admin(monkeypatch):
  monkeypatch.setattr(settings, "VENDEDOR_EMAIL", "Vendedor@Exemplo.com")
  monkeypatch.setattr(settings, "VENDEDOR_SENHA", "senha-do-vendedor")
  db = _db()
  service.criar_vendedor_inicial(db)
  usuario = service.autenticar(db, "vendedor@exemplo.com", "senha-do-vendedor")
  assert usuario and usuario.vendedor is True and usuario.admin is False


def test_vendedor_inicial_nao_duplica_nem_cria_sem_env(monkeypatch):
  db = _db()
  monkeypatch.setattr(settings, "VENDEDOR_EMAIL", "")
  monkeypatch.setattr(settings, "VENDEDOR_SENHA", "")
  service.criar_vendedor_inicial(db)
  assert service.listar(db) == []
  monkeypatch.setattr(settings, "VENDEDOR_EMAIL", "v@exemplo.com")
  monkeypatch.setattr(settings, "VENDEDOR_SENHA", "senha-do-vendedor")
  service.criar_vendedor_inicial(db)
  service.criar_vendedor_inicial(db)
  assert len(service.listar(db)) == 1
