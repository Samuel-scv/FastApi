from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import settings

# check_same_thread só existe no SQLite.
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependência do FastAPI: uma sessão por requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def atualizar_esquema_sqlite() -> None:
    """Adiciona colunas novas em um galaxia.db criado por uma versão anterior.

    O create_all só cria tabelas que não existem; não altera as que já existem.
    Para um projeto maior o caminho certo é o Alembic — aqui basta isto.
    """
    if engine.dialect.name != "sqlite":
        return
    inspetor = inspect(engine)
    if "clientes" in inspetor.get_table_names():
        colunas = {c["name"] for c in inspetor.get_columns("clientes")}
        if "plano_vencimento" not in colunas:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE clientes ADD COLUMN plano_vencimento DATE"))
