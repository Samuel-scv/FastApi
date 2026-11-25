from typing import Literal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..core.paginacao import montar, paginar
from . import estoque as estoque_service


def listar(
    db: Session,
    pagina: int = 1,
    por_pagina: int = 20,
    q: str | None = None,
    genero: str | None = None,
    diretor: str | None = None,
    tipo: Literal["filme", "serie"] | None = None,
    disponivel: bool | None = None,
    ordenar_por: Literal["titulo", "nota", "ano", "preco_aluguel"] = "titulo",
) -> dict:
    query = db.query(models.Produto)
    if q:
        query = query.filter(models.Produto.titulo.ilike(f"%{q}%"))
    if genero:
        query = query.filter(models.Produto.genero.ilike(f"%{genero}%"))
    if diretor:
        query = query.filter(models.Produto.diretor.ilike(f"%{diretor}%"))
    if tipo:
        query = query.filter(models.Produto.tipo == tipo)
    if disponivel is not None:
        query = query.filter(models.Produto.estoque > 0 if disponivel else models.Produto.estoque == 0)
    query = query.order_by(models.Produto.titulo) if ordenar_por in ("titulo", "nota") else query.order_by(getattr(models.Produto, ordenar_por).desc())
    produtos, total = paginar(query, pagina, por_pagina)
    itens = [_com_avaliacao(db, p) for p in produtos]
    if ordenar_por == "nota":  # nota é calculada, não dá para ordenar no SQL
        itens.sort(key=lambda p: p.nota_media or 0, reverse=True)
    return montar(itens, total, pagina, por_pagina)


def _com_avaliacao(db: Session, produto: models.Produto) -> schemas.Produto:
    from . import avaliacoes as avaliacoes_service

    saida = schemas.Produto.model_validate(produto)
    saida.nota_media, saida.total_avaliacoes = avaliacoes_service.media_do_produto(db, produto.id)
    return saida


def obter(db: Session, produto_id: int) -> models.Produto:
    produto = db.get(models.Produto, produto_id)
    if not produto:
        raise HTTPException(404, "Título não encontrado no acervo.")
    return produto


def obter_com_avaliacao(db: Session, produto_id: int) -> schemas.Produto:
    return _com_avaliacao(db, obter(db, produto_id))


def criar(db: Session, dados: schemas.ProdutoCriar) -> models.Produto:
    valores = dados.model_dump()
    inicial = valores.pop("estoque")
    produto = models.Produto(**valores, estoque=0)
    db.add(produto)
    db.flush()
    if inicial:
        estoque_service.registrar_movimento(db, produto, "inicial", inicial, "Cadastro do título")
    db.commit()
    db.refresh(produto)
    return produto


def atualizar(db: Session, produto_id: int, dados: schemas.ProdutoAtualizar) -> models.Produto:
    produto = obter(db, produto_id)
    valores = dados.model_dump(exclude_unset=True)
    novo_estoque = valores.pop("estoque", None)
    for campo, valor in valores.items():
        setattr(produto, campo, valor)
    if novo_estoque is not None and novo_estoque != produto.estoque:  # editar o saldo vira um ajuste no histórico
        estoque_service.registrar_movimento(db, produto, "ajuste", novo_estoque - produto.estoque, "Edição do cadastro do título")
    db.commit()
    db.refresh(produto)
    return produto


def excluir(db: Session, produto_id: int) -> None:
    produto = obter(db, produto_id)
    alugado = (
        db.query(models.Aluguel)
        .filter(models.Aluguel.produto_id == produto_id, models.Aluguel.status != "devolvido")
        .first()
    )
    if alugado:
        raise HTTPException(409, "Há cópia alugada desse título. Receba a devolução antes de excluir.")
    tem_historico = (
        db.query(models.Aluguel).filter(models.Aluguel.produto_id == produto_id).first()
        or db.query(models.Venda).filter(models.Venda.produto_id == produto_id).first()
    )
    if tem_historico:
        raise HTTPException(
            409, "Esse título tem aluguéis/vendas no histórico e não pode ser excluído. Zere o estoque."
        )
    db.query(models.MovimentoEstoque).filter(models.MovimentoEstoque.produto_id == produto_id).delete()
    db.query(models.Pergunta).filter(models.Pergunta.produto_id == produto_id).delete()
    db.delete(produto)
    db.commit()
