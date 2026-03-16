from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.utils.helpers import formatar_data_hora
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.cadastro_caixa_window import CadastroCaixaWindow
from app_embalagem.views.cadastro_funcionario_window import CadastroFuncionarioWindow
from app_embalagem.views.dashboard_window import DashboardWindow
from app_embalagem.views.historico_window import HistoricoWindow
from app_embalagem.views.scanner_window import ScannerWindow


class PageAdmin(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.caixa_service = CaixaService()
        self.setWindowTitle(f"Página Admin - {usuario.nome}")
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self._atualizar_tabela_caixas()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._atualizar_tabela_caixas)
        self.timer.start(3000)

    def _montar_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Área de Administrador")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        botoes = QGridLayout()
        self.scanner_btn = QPushButton("Scanner")
        self.func_btn = QPushButton("Cadastro de Funcionário")
        self.caixa_btn = QPushButton("Cadastro de Caixa")
        self.dash_btn = QPushButton("Dashboard")
        self.hist_btn = QPushButton("Histórico")

        self.scanner_btn.clicked.connect(self.abrir_scanner)
        self.func_btn.clicked.connect(self.abrir_funcionarios)
        self.caixa_btn.clicked.connect(self.abrir_caixas)
        self.dash_btn.clicked.connect(self.abrir_dashboard)
        self.hist_btn.clicked.connect(self.abrir_historico)

        botoes.addWidget(self.scanner_btn, 0, 0)
        botoes.addWidget(self.func_btn, 0, 1)
        botoes.addWidget(self.caixa_btn, 1, 0)
        botoes.addWidget(self.dash_btn, 1, 1)
        botoes.addWidget(self.hist_btn, 2, 0, 1, 2)

        layout.addLayout(botoes)
        layout.addWidget(QLabel("Cadastros de caixas (tempo real)"))

        self.caixas_table = QTableWidget(0, 6)
        self.caixas_table.setHorizontalHeaderLabels(["Código", "Nº Pedido", "Artigo", "Metros", "Status", "Criada em"])
        self.caixas_table.verticalHeader().setVisible(False)
        self.caixas_table.setAlternatingRowColors(True)
        layout.addWidget(self.caixas_table)

        self.setLayout(layout)

    def _atualizar_tabela_caixas(self):
        session = get_session()
        try:
            caixas = self.caixa_service.listar_recentes(session, limite=40)
            self.caixas_table.setRowCount(len(caixas))
            for i, caixa in enumerate(caixas):
                self.caixas_table.setItem(i, 0, QTableWidgetItem(caixa.codigo_caixa))
                self.caixas_table.setItem(i, 1, QTableWidgetItem(caixa.arte))
                self.caixas_table.setItem(i, 2, QTableWidgetItem(caixa.artigo))
                self.caixas_table.setItem(i, 3, QTableWidgetItem(f"{caixa.metros:.2f}"))
                self.caixas_table.setItem(i, 4, QTableWidgetItem(caixa.status))
                self.caixas_table.setItem(i, 5, QTableWidgetItem(formatar_data_hora(caixa.data_criacao)))
            self.caixas_table.resizeColumnsToContents()
        finally:
            session.close()

    def abrir_scanner(self):
        self.w_scanner = ScannerWindow()
        self.w_scanner.show()

    def abrir_funcionarios(self):
        self.w_func = CadastroFuncionarioWindow()
        self.w_func.show()

    def abrir_caixas(self):
        self.w_caixa = CadastroCaixaWindow()
        self.w_caixa.show()

    def abrir_dashboard(self):
        self.w_dash = DashboardWindow()
        self.w_dash.show()

    def abrir_historico(self):
        self.w_hist = HistoricoWindow()
        self.w_hist.show()
