from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.auth import usuario_atual
from ..core.database import get_db
from ..core.seguranca import criar_token, ler_token
from ..services import usuarios as service

router = APIRouter(prefix="/auth", tags=["auth"])

_CREDENCIAIS_INVALIDAS = HTTPException(401, "E-mail ou senha inválidos.", headers={"WWW-Authenticate": "Bearer"})


def _tokens(usuario: models.Usuario) -> schemas.Token:
  return schemas.Token(access_token=criar_token(usuario.id, "access"), refresh_token=criar_token(usuario.id, "refresh"))


@router.post("/registrar", response_model=schemas.Usuario, status_code=201)
def registrar(dados: schemas.UsuarioCriar, db: Session = Depends(get_db)):
  """Cadastro público. Sempre cria um usuário comum; admin só pelo ADMIN_EMAIL do .env."""
  return service.criar(db, dados)


@router.post("/login", response_model=schemas.Token)
def login(dados: schemas.Login, db: Session = Depends(get_db)):
  usuario = service.autenticar(db, dados.email, dados.senha)
  if not usuario:
    raise _CREDENCIAIS_INVALIDAS
  return _tokens(usuario)


@router.post("/login-form", response_model=schemas.Token, include_in_schema=True)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  """Mesmo login, mas em formato de formulário (username = e-mail). É o que o botão Authorize do /docs usa."""
  usuario = service.autenticar(db, form.username, form.password)
  if not usuario:
    raise _CREDENCIAIS_INVALIDAS
  return schemas.Token(access_token=criar_token(usuario.id, "access"))


@router.post("/refresh", response_model=schemas.Token)
def renovar(dados: schemas.RefreshPedido, db: Session = Depends(get_db)):
  id_usuario = ler_token(dados.refresh_token, "refresh")
  usuario = db.get(models.Usuario, id_usuario) if id_usuario else None
  if not usuario or not usuario.ativo:
    raise HTTPException(401, "Refresh token inválido ou expirado.", headers={"WWW-Authenticate": "Bearer"})
  return schemas.Token(access_token=criar_token(usuario.id, "access"))


@router.get("/me", response_model=schemas.Usuario)
def eu(usuario: models.Usuario = Depends(usuario_atual)):
  return usuario
