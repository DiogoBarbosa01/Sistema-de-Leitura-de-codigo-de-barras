from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app_embalagem.views.cadastro_caixa_window import CadastroCaixaWindow
from app_embalagem.views.cadastro_funcionario_window import CadastroFuncionarioWindow
from app_embalagem.views.dashboard_window import DashboardWindow
from app_embalagem.views.historico_window import HistoricoWindow
from app_embalagem.views.scanner_window import ScannerWindow


class MainWindow(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"Controle de Embalagem - {usuario.nome}")
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Escolha uma opção:"))

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
        self.setLayout(layout)

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
