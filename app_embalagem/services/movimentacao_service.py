from sqlalchemy import desc, select

from app_embalagem.models.movimentacao import Movimentacao


class MovimentacaoService:
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
