from datetime import date, datetime, time, timedelta

from sqlalchemy import desc, func, select

from app_embalagem.models.funcionario import Funcionario
from app_embalagem.models.movimentacao import Movimentacao


class MovimentacaoService:
    ACAO_FINALIZOU = "finalizou_embalagem"

    def registrar(self, session, caixa_id: int, funcionario_id: int, acao: str, observacao: str | None = None):
        movimentacao = Movimentacao(
            caixa_id=caixa_id,
            funcionario_id=funcionario_id,
            acao=acao,
            observacao=observacao,
        )
        session.add(movimentacao)
        session.commit()
        return movimentacao

    def ultimas(self, session, limite: int = 10):
        stmt = select(Movimentacao).order_by(desc(Movimentacao.data_hora)).limit(limite)
        return session.scalars(stmt).all()

    def listar_por_caixa(self, session, caixa_id: int):
        stmt = select(Movimentacao).where(Movimentacao.caixa_id == caixa_id).order_by(desc(Movimentacao.data_hora))
        return session.scalars(stmt).all()

    def total_finalizadas_no_dia(self, session, dia_ref: date) -> int:
        inicio = datetime.combine(dia_ref, time.min)
        fim = datetime.combine(dia_ref, time.max)
        stmt = select(func.count(Movimentacao.id)).where(
            Movimentacao.acao == self.ACAO_FINALIZOU,
            Movimentacao.data_hora.between(inicio, fim),
        )
        return session.scalar(stmt) or 0

    def total_finalizadas_hoje(self, session) -> int:
        return self.total_finalizadas_no_dia(session, date.today())

    def total_finalizadas_ultimo_dia(self, session) -> int:
        return self.total_finalizadas_no_dia(session, date.today() - timedelta(days=1))

    def operadores_online(self, session, janela_minutos: int = 10):
        limite = datetime.utcnow() - timedelta(minutes=janela_minutos)
        stmt = (
            select(
                Funcionario.id,
                Funcionario.nome,
                func.count(Movimentacao.id).label("qtd"),
                func.max(Movimentacao.data_hora).label("ultima_atividade"),
            )
            .join(Movimentacao, Movimentacao.funcionario_id == Funcionario.id)
            .where(
                Funcionario.ativo.is_(True),
                Movimentacao.acao == self.ACAO_FINALIZOU,
                Movimentacao.data_hora >= limite,
            )
            .group_by(Funcionario.id, Funcionario.nome)
            .order_by(desc("ultima_atividade"))
        )
        return session.execute(stmt).all()
