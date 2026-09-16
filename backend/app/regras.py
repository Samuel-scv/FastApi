"""
Regras de negócio da locadora, na mesma lógica usada no frontend:

- Cada aluguel tem prazo (data_prevista). Passou do prazo sem devolver = atraso.
- Multa padrão: MULTA_POR_DIA por dia de atraso, com carência opcional do plano.
- Cliente com aluguel em atraso fica bloqueado para novas locações/vendas fiado.
- Plano tem limite de locações por mês; passar do limite não bloqueia, apenas
  é informado para quem for cobrar a parte excedente como avulso.
- Plano pode dar dias extras de prazo (dias_bonus).
"""
from datetime import date

from sqlalchemy.orm import Session

from . import models

MULTA_POR_DIA = 3.5


def dias_de_atraso(aluguel: models.Aluguel, ate: date | None = None) -> int:
    referencia = aluguel.data_devolucao or ate or date.today()
    diff = (referencia - aluguel.data_prevista).days
    return max(0, diff)


def calcular_multa(aluguel: models.Aluguel, ate: date | None = None) -> float:
    dias = dias_de_atraso(aluguel, ate)
    carencia = 0
    if aluguel.cliente and aluguel.cliente.plano:
        carencia = aluguel.cliente.plano.carencia_multa_dias or 0
    dias_cobrados = max(0, dias - carencia)
    return round(dias_cobrados * MULTA_POR_DIA, 2)


def esta_atrasado(aluguel: models.Aluguel) -> bool:
    return aluguel.status != "devolvido" and dias_de_atraso(aluguel) > 0


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
