"""Dependências do FastAPI para proteger rotas."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .. import models
from .database import get_db
from .seguranca import ler_token

# tokenUrl faz o botão "Authorize" do /docs funcionar (usa o login por formulário).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login-form")


def usuario_atual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
  id_usuario = ler_token(token, "access")
  usuario = db.get(models.Usuario, id_usuario) if id_usuario else None
  if not usuario or not usuario.ativo:
    raise HTTPException(401, "Token inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"})
  return usuario


def exigir_admin(usuario: models.Usuario = Depends(usuario_atual)) -> models.Usuario:
  if not usuario.admin:
    raise HTTPException(403, "Apenas administradores podem fazer isso.")
  return usuario


def exigir_vendedor(usuario: models.Usuario = Depends(usuario_atual)) -> models.Usuario:
  """Equipe da loja (vendedor ou admin). Cliente comum, que só se cadastrou no site, não passa."""
  if not (usuario.vendedor or usuario.admin):
    raise HTTPException(403, "Apenas vendedores podem fazer isso.")
  return usuario
