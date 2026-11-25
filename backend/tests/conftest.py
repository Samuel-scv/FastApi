import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.core.database import Base, get_db
from app.core.seguranca import criar_token, hash_senha
from app.main import app


@pytest.fixture()
def client():
    """API com um banco SQLite em memória, novo a cada teste."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    Sessao = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def _get_db():
        db = Sessao()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    # Sem `with`: não dispara o lifespan, então o seed não roda nos testes.
    db = Sessao()
    admin = models.Usuario(nome="Admin", email="admin@teste.com", senha_hash=hash_senha("senha1234"), admin=True)
    db.add(admin)
    db.commit()
    token = criar_token(admin.id)
    db.close()
    c = TestClient(app)
    c.headers["Authorization"] = f"Bearer {token}"  # os testes antigos rodam logados como admin
    yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def anonimo(client):
    """Mesma API/banco do `client`, mas sem token."""
    return TestClient(app)
