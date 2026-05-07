import re
import unicodedata
from datetime import date, datetime, time, timedelta

from sqlalchemy import desc, func, select

from app_embalagem.models.caixa import Caixa
from app_embalagem.models.movimentacao import Movimentacao
from app_embalagem.services.barcode_service import BarcodeService
from app_embalagem.models.usuario import Usuario


class CaixaService:
    STATUS_CRIADA = "criada"
    STATUS_EMBALANDO = "embalando"
    STATUS_EMBALADA = "embalada"

    @staticmethod
    def _mes_para_letra(data_ref: datetime) -> str:
        return chr(ord("A") + data_ref.month - 1)

    @staticmethod
    def _duas_letras_funcionario(nome_funcionario: str) -> str:
        nome = unicodedata.normalize("NFKD", nome_funcionario).encode("ascii", "ignore").decode("ascii")
        letras = re.sub(r"[^A-Za-z]", "", nome).upper()
        return (letras[:2] or "XX").ljust(2, "X")

    @staticmethod
    def _matricula_4(matricula: str) -> str:
        digitos = re.sub(r"\D", "", matricula)
        return (digitos[-4:] if digitos else "0000").rjust(4, "0")

    def gerar_proximo_codigo(self, session, nome_funcionario: str, matricula: str) -> tuple[str, str, str]:
        agora = datetime.now()
        ano = agora.strftime("%y")
        dia = agora.strftime("%d")
        mes_letra = self._mes_para_letra(agora)
        sigla2 = self._duas_letras_funcionario(nome_funcionario)
        matricula4 = self._matricula_4(matricula)

        total = session.scalar(select(func.count(Caixa.id))) or 0
        uid = f"{total + 1:06d}"
        codigo = f"CX-{ano}{dia}{mes_letra}{sigla2}{matricula4}{uid}"
        return codigo, sigla2, uid

    def criar_caixa(
        self,
        session,
        numero_pedido: str,
        artigo: str,
        cor: str,
        largura: str,
        emendas: int,
        metros: float,
        nome_funcionario: str,
        matricula: str,
    ) -> tuple[Caixa, str]:
        codigo, sigla, _uid = self.gerar_proximo_codigo(session, nome_funcionario, matricula)
        caixa = Caixa(
            codigo_caixa=codigo,
            arte=numero_pedido,
            artigo=artigo,
            cor=cor,
            largura=largura,
            emendas=emendas,
            metros=metros,
            nome_funcionario=nome_funcionario,
            sigla_funcionario=sigla,
            status=self.STATUS_CRIADA,
        )
        caixa.barcode_png = BarcodeService.gerar_codigo_barras_bytes(codigo)
        session.add(caixa)
        session.commit()
        session.refresh(caixa)
        caminho_barcode = f"db://caixas/{caixa.id}/barcode"
        return caixa, caminho_barcode

    def listar_recentes(self, session, limite: int = 20):
        stmt = select(Caixa).order_by(desc(Caixa.data_criacao)).limit(limite)
        return session.scalars(stmt).all()

    def buscar_por_codigo(self, session, codigo: str) -> Caixa | None:
        return session.scalar(select(Caixa).where(Caixa.codigo_caixa == codigo))

    def atualizar_status(self, session, caixa: Caixa, status: str):
        caixa.status = status
        session.commit()

    def total_embaladas_hoje(self, session) -> int:
        inicio = datetime.combine(date.today(), time.min)
        fim = datetime.combine(date.today(), time.max)
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

    def total_cadastradas_no_dia(self, session, dia_ref: date) -> int:
        inicio = datetime.combine(dia_ref, time.min)
        fim = datetime.combine(dia_ref, time.max)
        stmt = select(func.count(Caixa.id)).where(Caixa.data_criacao.between(inicio, fim))
        return session.scalar(stmt) or 0

    def total_cadastradas_hoje(self, session) -> int:
        return self.total_cadastradas_no_dia(session, date.today())

    def total_cadastradas_ultimo_dia(self, session) -> int:
        return self.total_cadastradas_no_dia(session, date.today() - timedelta(days=1))

    def operadores_online(self, session, janela_segundos=15):

        limite = datetime.now() - timedelta(seconds=janela_segundos)

        usuarios = (session.query(Usuario).filter(Usuario.ultima_atividade >= limite).all()
    )
        return usuarios or []
