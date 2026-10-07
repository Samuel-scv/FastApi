"""Configurações da aplicação.

Os valores vêm do arquivo .env (se existir) e têm padrão sensato, então a API
sobe mesmo sem .env. Veja o .env.example para as chaves disponíveis.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]  # pasta backend/
load_dotenv(BASE_DIR / ".env")


def _lista(valor: str) -> list[str]:
    return [item.strip() for item in valor.split(",") if item.strip()]


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'galaxia.db'}")
    CORS_ORIGINS: list[str] = _lista(os.getenv("CORS_ORIGINS", "*"))
    MULTA_POR_DIA: float = float(os.getenv("MULTA_POR_DIA", "3.5"))
    DIAS_PLANO: int = int(os.getenv("DIAS_PLANO", "30"))  # duração de cada mensalidade


settings = Settings()
