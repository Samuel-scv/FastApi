"""
Regras de negócio da locadora:

- Cada aluguel tem prazo (data_prevista). Passou do prazo sem devolver = atraso.
- Multa: MULTA_POR_DIA por dia de atraso, com carência opcional do plano.
- Cliente com aluguel em atraso fica bloqueado para novas locações.
- Plano vale até `plano_vencimento`. Vencido, o cliente perde os benefícios
  (dias extras de prazo e carência de multa) até renovar.
- Plano tem limite de locações por mês; passar do limite não bloqueia, só
  avisa (`limite_atingido`) para o balcão cobrar o excedente como avulso.
"""
from datetime import date

from sqlalchemy.orm import Session

from . import models
from .core.config import settings

MULTA_POR_DIA = settings.MULTA_POR_DIA


# ---------- plano ----------
def plano_vigente(cliente: models.Cliente, referencia: date | None = None) -> models.Plano | None:
    """Plano do cliente se a mensalidade ainda vale na data; senão None."""
    referencia = referencia or date.today()
    if not cliente or not cliente.plano:
        return None
    if cliente.plano_vencimento is not None and cliente.plano_vencimento < referencia:
        return None
    return cliente.plano


def status_do_plano(cliente: models.Cliente, referencia: date | None = None) -> str:
    """'sem_plano' | 'ativo' | 'vencido'."""
    if not cliente.plano_id:
        return "sem_plano"
    return "ativo" if plano_vigente(cliente, referencia) else "vencido"


# ---------- aluguel ----------
def dias_de_atraso(aluguel: models.Aluguel, ate: date | None = None) -> int:
    referencia = aluguel.data_devolucao or ate or date.today()
    return max(0, (referencia - aluguel.data_prevista).days)


def calcular_multa(aluguel: models.Aluguel, ate: date | None = None) -> float:
    referencia = aluguel.data_devolucao or ate or date.today()
    dias = dias_de_atraso(aluguel, ate)
    plano = plano_vigente(aluguel.cliente, referencia)
    carencia = (plano.carencia_multa_dias or 0) if plano else 0
    return round(max(0, dias - carencia) * MULTA_POR_DIA, 2)


def esta_atrasado(aluguel: models.Aluguel) -> bool:
    return aluguel.status != "devolvido" and dias_de_atraso(aluguel) > 0


# ---------- cliente ----------
def cliente_bloqueado(db: Session, cliente_id: int) -> bool:
    pendencias = (
        db.query(models.Aluguel)
        .filter(models.Aluguel.cliente_id == cliente_id, models.Aluguel.status != "devolvido")
        .all()
    )
    return any(esta_atrasado(a) for a in pendencias)


def locacoes_no_mes(db: Session, cliente_id: int, referencia: date | None = None) -> int:
    referencia = referencia or date.today()
    inicio_mes = referencia.replace(day=1)
    return (
        db.query(models.Aluguel)
        .filter(
            models.Aluguel.cliente_id == cliente_id,
            models.Aluguel.data_retirada >= inicio_mes,
        )
        .count()
    )


def limite_atingido(db: Session, cliente: models.Cliente) -> bool:
    plano = plano_vigente(cliente)
    return bool(plano) and locacoes_no_mes(db, cliente.id) >= plano.limite_mensal
