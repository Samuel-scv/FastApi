from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.auth import exigir_admin
from ..core.database import get_db
from ..services import usuarios as service

router = APIRouter(prefix="/usuarios", tags=["usuarios"], dependencies=[Depends(exigir_admin)])


@router.get("", response_model=list[schemas.Usuario])
def listar_usuarios(db: Session = Depends(get_db)):
  return service.listar(db)


@router.patch("/{usuario_id}", response_model=schemas.Usuario)
def atualizar_usuario(usuario_id: int, dados: schemas.UsuarioAtualizar, admin: models.Usuario = Depends(exigir_admin), db: Session = Depends(get_db)):
  """Promove a vendedor/admin ou desativa uma conta."""
  return service.atualizar(db, usuario_id, dados, admin)
