from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UsuarioCriar(BaseModel):
  model_config = ConfigDict(str_strip_whitespace=True)

  nome: str = Field(min_length=1)
  email: EmailStr
  senha: str = Field(min_length=8, max_length=72)

  @field_validator("senha")
  @classmethod
  def senha_cabe_no_bcrypt(cls, v: str) -> str:
    if len(v.encode("utf-8")) > 72:  # o bcrypt só lê os 72 primeiros bytes
      raise ValueError("A senha pode ter no máximo 72 bytes.")
    return v


class Login(BaseModel):
  email: EmailStr
  senha: str


class Usuario(BaseModel):
  model_config = ConfigDict(from_attributes=True)

  id: int
  nome: str
  email: str
  ativo: bool
  admin: bool
  vendedor: bool


class Token(BaseModel):
  access_token: str
  refresh_token: Optional[str] = None
  token_type: str = "bearer"


class RefreshPedido(BaseModel):
  refresh_token: str


class UsuarioAtualizar(BaseModel):
  vendedor: Optional[bool] = None
  admin: Optional[bool] = None
  ativo: Optional[bool] = None
