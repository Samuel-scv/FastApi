"""Configurações da aplicação.

Os valores vêm do arquivo .env (se existir) e têm padrão sensato, então a API
sobe mesmo sem .env. Veja o .env.example para as chaves disponíveis.
"""
import os
import secrets
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy.engine import make_url

BASE_DIR = Path(__file__).resolve().parents[2]  # pasta backend/
load_dotenv(BASE_DIR / ".env")


def _lista(valor: str) -> list[str]:
    return [item.strip() for item in valor.split(",") if item.strip()]


def _database_url() -> str:
    data_dir = os.getenv("APP_DATA_DIR")
    padrao = Path(data_dir) / "galaxia.db" if data_dir else BASE_DIR / "galaxia.db"
    url = os.getenv("DATABASE_URL", f"sqlite:///{padrao}")
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
    # Auth. Sem SECRET_KEY no .env, uma chave aleatória é gerada a cada start (os logins caem ao reiniciar).
    SECRET_KEY: str = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "")  # se preenchidos, cria o 1º admin no start
    ADMIN_SENHA: str = os.getenv("ADMIN_SENHA", "")


settings = Settings()