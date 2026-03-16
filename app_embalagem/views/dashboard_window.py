from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select

from app_embalagem.database.connection import get_session
from app_embalagem.models.funcionario import Funcionario
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.services.movimentacao_service import MovimentacaoService
from app_embalagem.utils.helpers import formatar_data_hora


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.caixa_service = CaixaService()
        self.mov_service = MovimentacaoService()
        self.setWindowTitle("Dashboard")
        self._montar_ui()
        self._carregar()

    def _montar_ui(self):
        layout = QVBoxLayout()
        self.total_hoje_label = QLabel()
        self.pendentes_label = QLabel()
        self.producao_label = QLabel()

        self.mov_table = QTableWidget(0, 4)
        self.mov_table.setHorizontalHeaderLabels(["Caixa", "Funcionário", "Ação", "Data/Hora"])

        layout.addWidget(self.total_hoje_label)
        layout.addWidget(self.pendentes_label)
        layout.addWidget(self.producao_label)
        layout.addWidget(QLabel("Últimas movimentações"))
        layout.addWidget(self.mov_table)
        self.setLayout(layout)

    def _carregar(self):
        session = get_session()
        try:
            total_hoje = self.caixa_service.total_embaladas_hoje(session)
            pendentes = self.caixa_service.total_pendentes(session)
            producao = self.caixa_service.producao_por_funcionario(session)

            self.total_hoje_label.setText(f"Caixas embaladas hoje: {total_hoje}")
            self.pendentes_label.setText(f"Caixas pendentes: {pendentes}")

            linhas_producao = []
            for funcionario_id, qtd in producao:
                funcionario = session.scalar(select(Funcionario).where(Funcionario.id == funcionario_id))
                nome = funcionario.nome if funcionario else f"ID {funcionario_id}"
                linhas_producao.append(f"{nome}: {qtd}")
            self.producao_label.setText("Produção por funcionário: " + (", ".join(linhas_producao) if linhas_producao else "-"))

            ultimas = self.mov_service.ultimas(session)
            self.mov_table.setRowCount(len(ultimas))
            for i, mov in enumerate(ultimas):
                self.mov_table.setItem(i, 0, QTableWidgetItem(mov.caixa.codigo_caixa if mov.caixa else "-"))
                self.mov_table.setItem(i, 1, QTableWidgetItem(mov.funcionario.nome if mov.funcionario else "-"))
                self.mov_table.setItem(i, 2, QTableWidgetItem(mov.acao))
                self.mov_table.setItem(i, 3, QTableWidgetItem(formatar_data_hora(mov.data_hora)))
        finally:
            session.close()
