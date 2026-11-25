from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.config import settings
from ..core.seguranca import hash_senha, verificar_senha

# Usado quando o e-mail não existe, para o tempo de resposta não revelar se a conta existe.
_HASH_FALSO = hash_senha("senha-falsa-para-igualar-o-tempo")


def obter_por_email(db: Session, email: str) -> models.Usuario | None:
  return db.query(models.Usuario).filter(models.Usuario.email == email.lower()).first()


def criar(db: Session, dados: schemas.UsuarioCriar, admin: bool = False) -> models.Usuario:
  if obter_por_email(db, dados.email):
    raise HTTPException(409, "Já existe um usuário com esse e-mail.")
  usuario = models.Usuario(nome=dados.nome, email=dados.email.lower(), senha_hash=hash_senha(dados.senha), admin=admin)
  db.add(usuario)
  db.commit()
  db.refresh(usuario)
  return usuario


def autenticar(db: Session, email: str, senha: str) -> models.Usuario | None:
  usuario = obter_por_email(db, email)
  senha_ok = verificar_senha(senha, usuario.senha_hash if usuario else _HASH_FALSO)
  if not usuario or not senha_ok or not usuario.ativo:
    return None
  return usuario


def criar_admin_inicial(db: Session) -> None:
  """Cria o primeiro admin a partir do .env (ADMIN_EMAIL / ADMIN_SENHA), se ainda não existir."""
  if not settings.ADMIN_EMAIL or not settings.ADMIN_SENHA or obter_por_email(db, settings.ADMIN_EMAIL):
    return
  criar(db, schemas.UsuarioCriar(nome="Administrador", email=settings.ADMIN_EMAIL, senha=settings.ADMIN_SENHA), admin=True)


def listar(db: Session) -> list[models.Usuario]:
  return db.query(models.Usuario).order_by(models.Usuario.nome).all()


def atualizar(db: Session, usuario_id: int, dados: schemas.UsuarioAtualizar, quem: models.Usuario) -> models.Usuario:
  usuario = db.get(models.Usuario, usuario_id)
  if not usuario:
    raise HTTPException(404, "Usuário não encontrado.")
  valores = {campo: valor for campo, valor in dados.model_dump().items() if valor is not None}
  if usuario.id == quem.id and (valores.get("ativo") is False or valores.get("admin") is False):
    raise HTTPException(409, "Você não pode desativar nem tirar o admin da própria conta.")
  for campo, valor in valores.items():
    setattr(usuario, campo, valor)
  db.commit()
  db.refresh(usuario)
  return usuario
