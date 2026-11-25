"""Senhas (bcrypt) e tokens JWT (PyJWT)."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from .config import settings


def hash_senha(senha: str) -> str:
  return bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
  try:
    return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
  except ValueError:
    return False


def criar_token(id_usuario: int, tipo: str = "access") -> str:
  """tipo = 'access' (curto, vai em todo request) ou 'refresh' (longo, só serve para renovar)."""
  duracao = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) if tipo == "access" else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
  payload = {"sub": str(id_usuario), "tipo": tipo, "exp": datetime.now(timezone.utc) + duracao}
  return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def ler_token(token: str, tipo: str) -> int | None:
  """Devolve o id do usuário se o token for válido, do tipo certo e não expirado; senão None."""
  try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    if payload.get("tipo") != tipo:
      return None
    return int(payload["sub"])
  except (jwt.PyJWTError, KeyError, ValueError):
    return None
