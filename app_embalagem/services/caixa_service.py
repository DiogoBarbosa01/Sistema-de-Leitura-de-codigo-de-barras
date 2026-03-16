import re
import unicodedata
from datetime import date, datetime

from sqlalchemy import func, select

from app_embalagem.models.caixa import Caixa
from app_embalagem.models.movimentacao import Movimentacao
from app_embalagem.services.barcode_service import BarcodeService


class CaixaService:
    STATUS_CRIADA = "criada"
    STATUS_EMBALANDO = "embalando"
    STATUS_EMBALADA = "embalada"

    @staticmethod
    def _extrair_sigla_funcionario(nome_funcionario: str) -> str:
        nome = unicodedata.normalize("NFKD", nome_funcionario).encode("ascii", "ignore").decode("ascii")
        letras = re.sub(r"[^A-Za-z]", "", nome).upper()
        sigla = (letras[:4] or "XXXX").ljust(4, "X")
        return sigla

    def gerar_proximo_codigo(self, session, nome_funcionario: str) -> tuple[str, str, int]:
        total = session.scalar(select(func.count(Caixa.id))) or 0
        sequencia = total + 1
        sigla = self._extrair_sigla_funcionario(nome_funcionario)
        data_codigo = datetime.now().strftime("%d%m%y")
        codigo = f"CX-{data_codigo}-{sigla}-{sequencia:04d}"
        return codigo, sigla, sequencia

    def criar_caixa(self, session, arte: str, artigo: str, metros: float, nome_funcionario: str) -> tuple[Caixa, str]:
        codigo, sigla, _ = self.gerar_proximo_codigo(session, nome_funcionario)
        caixa = Caixa(
            codigo_caixa=codigo,
            arte=arte,
            artigo=artigo,
            metros=metros,
            sigla_funcionario=sigla,
            status=self.STATUS_CRIADA,
        )
        session.add(caixa)
        session.commit()
        session.refresh(caixa)
        caminho_barcode = BarcodeService.gerar_codigo_barras(codigo)
        return caixa, caminho_barcode

    def buscar_por_codigo(self, session, codigo: str) -> Caixa | None:
        return session.scalar(select(Caixa).where(Caixa.codigo_caixa == codigo))

    def atualizar_status(self, session, caixa: Caixa, status: str):
        caixa.status = status
        session.commit()

    def total_embaladas_hoje(self, session) -> int:
        inicio = datetime.combine(date.today(), datetime.min.time())
        fim = datetime.combine(date.today(), datetime.max.time())
        stmt = select(func.count(Caixa.id)).where(Caixa.status == self.STATUS_EMBALADA, Caixa.data_criacao.between(inicio, fim))
        return session.scalar(stmt) or 0

    def total_pendentes(self, session) -> int:
        stmt = select(func.count(Caixa.id)).where(Caixa.status != self.STATUS_EMBALADA)
        return session.scalar(stmt) or 0

    def producao_por_funcionario(self, session):
        stmt = (
            select(Movimentacao.funcionario_id, func.count(Movimentacao.id))
            .where(Movimentacao.acao == "finalizou_embalagem")
            .group_by(Movimentacao.funcionario_id)
        )
        return session.execute(stmt).all()
