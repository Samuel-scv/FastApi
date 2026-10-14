"""Configurações da aplicação.

Os valores vêm do arquivo .env (se existir) e têm padrão sensato, então a API
sobe mesmo sem .env. Veja o .env.example para as chaves disponíveis.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

BASE_DIR = Path(__file__).resolve().parents[2]  # pasta backend/
load_dotenv(BASE_DIR / ".env")


def _lista(valor: str) -> list[str]:
    return [item.strip() for item in valor.split(",") if item.strip()]


def _database_url() -> str:
    url = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'galaxia.db'}")
    data_dir = os.getenv("APP_DATA_DIR")
    if not data_dir or not url.startswith("sqlite:"):
        return url

    parsed_url = make_url(url)
    database = parsed_url.database
    if database and database != ":memory:" and not Path(database).is_absolute():
        database = str(Path(data_dir) / database)
        return parsed_url.set(database=database).render_as_string(hide_password=False)
    return url


class Settings:
    DATABASE_URL: str = _database_url()
    CORS_ORIGINS: list[str] = _lista(os.getenv("CORS_ORIGINS", "*"))
    MULTA_POR_DIA: float = float(os.getenv("MULTA_POR_DIA", "3.5"))
    DIAS_PLANO: int = int(os.getenv("DIAS_PLANO", "30"))  # duração de cada mensalidade


settings = Settings()
