from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app_embalagem.database.connection import get_session
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.services.movimentacao_service import MovimentacaoService
from app_embalagem.utils.helpers import formatar_data_hora


class HistoricoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.caixa_service = CaixaService()
        self.mov_service = MovimentacaoService()
        self.setWindowTitle("Histórico de Movimentações")
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("CX-000001")
        form.addRow("Código da caixa:", self.codigo_input)

        buscar_btn = QPushButton("Pesquisar")
        buscar_btn.clicked.connect(self._buscar)

        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Funcionário", "Ação", "Data/Hora"])

        layout.addLayout(form)
        layout.addWidget(buscar_btn)
        layout.addWidget(QLabel("Movimentações da caixa"))
        layout.addWidget(self.tabela)
        self.setLayout(layout)

    def _buscar(self):
        codigo = self.codigo_input.text().strip().upper()
        if not codigo:
            QMessageBox.warning(self, "Validação", "Informe o código da caixa.")
            return

        session = get_session()
        try:
            caixa = self.caixa_service.buscar_por_codigo(session, codigo)
            if not caixa:
                QMessageBox.warning(self, "Não encontrado", "Caixa não localizada.")
                return

            movimentacoes = self.mov_service.listar_por_caixa(session, caixa.id)
            self.tabela.setRowCount(len(movimentacoes))
            for i, mov in enumerate(movimentacoes):
                self.tabela.setItem(i, 0, QTableWidgetItem(mov.funcionario.nome if mov.funcionario else "-"))
                self.tabela.setItem(i, 1, QTableWidgetItem(mov.acao))
                self.tabela.setItem(i, 2, QTableWidgetItem(formatar_data_hora(mov.data_hora)))
        finally:
            session.close()
