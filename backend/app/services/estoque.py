from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.paginacao import montar, paginar


def registrar_movimento(db: Session, produto: models.Produto, tipo: str, quantidade: int, motivo: str = "", usuario_id: int | None = None, aluguel_id: int | None = None, venda_id: int | None = None) -> models.MovimentoEstoque:
  """Única porta de entrada para mudar `produto.estoque`: aplica a variação e grava o histórico. Não faz commit."""
  novo_saldo = produto.estoque + quantidade
  if novo_saldo < 0:
    raise HTTPException(409, f"Só há {produto.estoque} cópia(s) de '{produto.titulo}' na prateleira.")
  produto.estoque = novo_saldo
  movimento = models.MovimentoEstoque(produto_id=produto.id, tipo=tipo, quantidade=quantidade, saldo_apos=novo_saldo, motivo=motivo, usuario_id=usuario_id, aluguel_id=aluguel_id, venda_id=venda_id)
  db.add(movimento)
  if tipo in ("entrada", "devolucao") and quantidade > 0:
    from . import reservas as reservas_service

    reservas_service.promover_fila(db, produto)
  return movimento


def _produto(db: Session, produto_id: int) -> models.Produto:
  produto = db.get(models.Produto, produto_id)
  if not produto:
    raise HTTPException(404, "Título não encontrado no acervo.")
  return produto


def _serializar(movimento: models.MovimentoEstoque) -> schemas.MovimentoEstoque:
  saida = schemas.MovimentoEstoque.model_validate(movimento)
  saida.titulo = movimento.produto.titulo
  return saida


def _salvar(db: Session, movimento: models.MovimentoEstoque) -> schemas.MovimentoEstoque:
  db.commit()
  db.refresh(movimento)
  return _serializar(movimento)


def entrada(db: Session, produto_id: int, dados: schemas.EntradaEstoque, usuario_id: int) -> schemas.MovimentoEstoque:
  produto = _produto(db, produto_id)
  return _salvar(db, registrar_movimento(db, produto, "entrada", dados.quantidade, dados.motivo, usuario_id))


def perda(db: Session, produto_id: int, dados: schemas.PerdaEstoque, usuario_id: int) -> schemas.MovimentoEstoque:
  """Baixa de cópia danificada/extraviada. Só sai o que está na prateleira (cópia alugada: receba a devolução antes)."""
  produto = _produto(db, produto_id)
  return _salvar(db, registrar_movimento(db, produto, "perda", -dados.quantidade, dados.motivo, usuario_id))


def ajustar(db: Session, produto_id: int, dados: schemas.AjusteEstoque, usuario_id: int | None) -> schemas.MovimentoEstoque:
  """Inventário: iguala o estoque da prateleira à contagem real e registra a diferença."""
  produto = _produto(db, produto_id)
  diferenca = dados.saldo - produto.estoque
  if diferenca == 0:
    raise HTTPException(400, "O saldo informado já é o atual.")
  return _salvar(db, registrar_movimento(db, produto, "ajuste", diferenca, dados.motivo, usuario_id))


def listar_movimentos(db: Session, produto_id: int | None = None, tipo: str | None = None, pagina: int = 1, por_pagina: int = 20) -> dict:
  query = db.query(models.MovimentoEstoque)
  if produto_id is not None:
    query = query.filter(models.MovimentoEstoque.produto_id == produto_id)
  if tipo:
    query = query.filter(models.MovimentoEstoque.tipo == tipo)
  query = query.order_by(models.MovimentoEstoque.id.desc())
  movimentos, total = paginar(query, pagina, por_pagina)
  return montar([_serializar(m) for m in movimentos], total, pagina, por_pagina)


def resumo(db: Session, tipo: str | None = None, situacao: str | None = None) -> schemas.ResumoEstoque:
  alugadas_por_produto = dict(db.query(models.Aluguel.produto_id, func.count(models.Aluguel.id)).filter(models.Aluguel.status != "devolvido").group_by(models.Aluguel.produto_id).all())
  query = db.query(models.Produto).order_by(models.Produto.titulo)
  if tipo:
    query = query.filter(models.Produto.tipo == tipo)
  itens = []
  for p in query.all():
    alugadas = alugadas_por_produto.get(p.id, 0)
    total = p.estoque + alugadas
    sit = "zerado" if total == 0 else "baixo" if total <= p.estoque_minimo else "ok"
    itens.append(schemas.ItemEstoque(produto_id=p.id, titulo=p.titulo, tipo=p.tipo, disponivel=p.estoque, alugadas=alugadas, total_acervo=total, estoque_minimo=p.estoque_minimo, situacao=sit, todas_alugadas=total > 0 and p.estoque == 0))
  if situacao:
    itens = [i for i in itens if i.situacao == situacao]
  return schemas.ResumoEstoque(titulos=len(itens), copias_disponiveis=sum(i.disponivel for i in itens), copias_alugadas=sum(i.alugadas for i in itens), titulos_baixos=sum(i.situacao == "baixo" for i in itens), titulos_zerados=sum(i.situacao == "zerado" for i in itens), itens=itens)


def sincronizar_saldos_iniciais(db: Session) -> None:
  """Bancos criados antes do controle de estoque: grava o saldo atual como ponto de partida do histórico."""
  com_historico = {pid for (pid,) in db.query(models.MovimentoEstoque.produto_id).distinct()}
  for p in db.query(models.Produto).filter(models.Produto.estoque > 0).all():
    if p.id not in com_historico:
      db.add(models.MovimentoEstoque(produto_id=p.id, tipo="inicial", quantidade=p.estoque, saldo_apos=p.estoque, motivo="Saldo anterior ao controle de estoque"))
  db.commit()
