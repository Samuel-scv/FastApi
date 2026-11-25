from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, regras, schemas


def faturamento(db: Session, inicio: date | None, fim: date | None) -> schemas.Faturamento:
  fim = fim or date.today()
  inicio = inicio or fim.replace(day=1)
  if inicio > fim:
    raise HTTPException(400, "A data de início não pode ser depois da data de fim.")

  alugueis = db.query(models.Aluguel).filter(models.Aluguel.data_retirada >= inicio, models.Aluguel.data_retirada <= fim).all()
  vendas = db.query(models.Venda).filter(models.Venda.data >= inicio, models.Venda.data <= fim).all()
  devolvidos_no_periodo = db.query(models.Aluguel).filter(models.Aluguel.data_devolucao >= inicio, models.Aluguel.data_devolucao <= fim).all()

  por_dia: dict[date, dict[str, float]] = {}

  def soma(dia: date, chave: str, valor: float) -> None:
    linha = por_dia.setdefault(dia, {"aluguel": 0.0, "venda": 0.0, "multa": 0.0})
    linha[chave] += valor

  for a in alugueis:
    soma(a.data_retirada, "aluguel", a.valor)
  for v in vendas:
    soma(v.data, "venda", v.valor_total)
  for a in devolvidos_no_periodo:
    if a.multa_paga:
      soma(a.data_devolucao, "multa", a.multa_paga)

  total_aluguel = sum(a.valor for a in alugueis)
  total_venda = sum(v.valor_total for v in vendas)
  total_multa = sum(a.multa_paga for a in devolvidos_no_periodo)
  total_geral = round(total_aluguel + total_venda + total_multa, 2)
  transacoes = len(alugueis) + len(vendas)

  pontos = [
    schemas.PontoFaturamento(data=dia, aluguel=round(v["aluguel"], 2), venda=round(v["venda"], 2), multa=round(v["multa"], 2), total=round(sum(v.values()), 2))
    for dia, v in sorted(por_dia.items())
  ]
  return schemas.Faturamento(
    inicio=inicio, fim=fim,
    total_aluguel=round(total_aluguel, 2), total_venda=round(total_venda, 2), total_multa=round(total_multa, 2), total_geral=total_geral,
    quantidade_alugueis=len(alugueis), quantidade_vendas=len(vendas),
    ticket_medio=round(total_geral / transacoes, 2) if transacoes else 0,
    por_dia=pontos,
  )


def mais_alugados(db: Session, limite: int, inicio: date | None, fim: date | None) -> list[schemas.ItemRanking]:
  query = db.query(models.Aluguel.produto_id, func.count(models.Aluguel.id), func.sum(models.Aluguel.valor)).join(models.Produto)
  if inicio:
    query = query.filter(models.Aluguel.data_retirada >= inicio)
  if fim:
    query = query.filter(models.Aluguel.data_retirada <= fim)
  linhas = query.group_by(models.Aluguel.produto_id).order_by(func.count(models.Aluguel.id).desc()).limit(limite).all()
  return [schemas.ItemRanking(produto_id=pid, titulo=db.get(models.Produto, pid).titulo, quantidade=qtd, valor=round(valor or 0, 2)) for pid, qtd, valor in linhas]


def mais_vendidos(db: Session, limite: int, inicio: date | None, fim: date | None) -> list[schemas.ItemRanking]:
  query = db.query(models.Venda.produto_id, func.sum(models.Venda.quantidade), func.sum(models.Venda.valor_total))
  if inicio:
    query = query.filter(models.Venda.data >= inicio)
  if fim:
    query = query.filter(models.Venda.data <= fim)
  linhas = query.group_by(models.Venda.produto_id).order_by(func.sum(models.Venda.quantidade).desc()).limit(limite).all()
  return [schemas.ItemRanking(produto_id=pid, titulo=db.get(models.Produto, pid).titulo, quantidade=qtd or 0, valor=round(valor or 0, 2)) for pid, qtd, valor in linhas]


def dashboard(db: Session) -> schemas.ResumoDashboard:
  hoje = date.today()
  fat_mes = faturamento(db, hoje.replace(day=1), hoje)
  ativos = db.query(models.Aluguel).filter(models.Aluguel.status == "ativo").all()
  atrasados = sum(1 for a in ativos if regras.esta_atrasado(a))
  produtos = db.query(models.Produto).all()
  alugadas_por_produto = dict(db.query(models.Aluguel.produto_id, func.count(models.Aluguel.id)).filter(models.Aluguel.status != "devolvido").group_by(models.Aluguel.produto_id).all())
  baixo = zerado = 0
  for p in produtos:
    total = p.estoque + alugadas_por_produto.get(p.id, 0)
    if total == 0:
      zerado += 1
    elif total <= p.estoque_minimo:
      baixo += 1
  clientes_bloqueados = sum(1 for c in db.query(models.Cliente).all() if regras.cliente_bloqueado(db, c.id))
  return schemas.ResumoDashboard(
    faturamento_mes_atual=fat_mes.total_geral,
    alugueis_ativos=len(ativos),
    alugueis_atrasados=atrasados,
    titulos_estoque_baixo=baixo,
    titulos_estoque_zerado=zerado,
    perguntas_pendentes=db.query(models.Pergunta).filter(models.Pergunta.resposta.is_(None)).count(),
    reservas_aguardando=db.query(models.Reserva).filter(models.Reserva.status == "aguardando").count(),
    clientes_bloqueados=clientes_bloqueados,
  )
