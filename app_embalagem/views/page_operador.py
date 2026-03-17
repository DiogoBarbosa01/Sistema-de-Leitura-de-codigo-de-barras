from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.codigos_barras_window import CodigosBarrasWindow
from app_embalagem.views.dashboard_window import DashboardWindow
from app_embalagem.views.historico_window import HistoricoWindow
from app_embalagem.views.scanner_window import ScannerWindow


class PageOperador(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle(f"Página Operador - {usuario.nome}")
        self.resize(760, 420)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _montar_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Área do Operador")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        subtitulo = QLabel(f"Olá, {self.usuario.nome}. Selecione a ação desejada.")
        subtitulo.setObjectName("subtitulo")
        layout.addWidget(subtitulo)

        botoes = QGridLayout()
        self.scanner_btn = QPushButton("Scanner")
        self.dash_btn = QPushButton("Dashboard")
        self.hist_btn = QPushButton("Histórico")
        self.codigos_btn = QPushButton("Códigos de Barras")

        self.scanner_btn.clicked.connect(self.abrir_scanner)
        self.dash_btn.clicked.connect(self.abrir_dashboard)
        self.hist_btn.clicked.connect(self.abrir_historico)
        self.codigos_btn.clicked.connect(self.abrir_codigos)

        botoes.addWidget(self.scanner_btn, 0, 0)
        botoes.addWidget(self.dash_btn, 0, 1)
        botoes.addWidget(self.hist_btn, 1, 0)
        botoes.addWidget(self.codigos_btn, 1, 1)

        layout.addLayout(botoes)
        self.setLayout(layout)

    def abrir_scanner(self):
        self.w_scanner = ScannerWindow()
        self.w_scanner.show()

    def abrir_dashboard(self):
        self.w_dash = DashboardWindow()
        self.w_dash.show()

    def abrir_historico(self):
        self.w_hist = HistoricoWindow()
        self.w_hist.show()

    def abrir_codigos(self):
        self.w_codigos = CodigosBarrasWindow()
        self.w_codigos.show()
