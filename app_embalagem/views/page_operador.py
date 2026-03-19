from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from app_embalagem.database.connection import get_session
from app_embalagem.services.mobile_request_service import MobileRequestService
from app_embalagem.services.mobile_usb_service import MobileUsbService
from app_embalagem.services.scan_service import ScanService
from app_embalagem.utils.sound import beep_scan
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.caixa_detalhes_dialog import CaixaDetalhesDialog
from app_embalagem.views.codigos_barras_window import CodigosBarrasWindow
from app_embalagem.views.dashboard_window import DashboardWindow
from app_embalagem.views.scanner_window import ScannerWindow



class PageOperador(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.scan_service = ScanService()
        self.mobile_usb_service = MobileUsbService()
        self.mobile_request_service = MobileRequestService()
        self.setWindowTitle(f"Página Operador - {usuario.nome}")
        self.resize(760, 420)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
      
       

        try:
            self.mobile_request_service.iniciar()
        except Exception:
            pass

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._monitorar)
        self.timer.start(1800)

    def _montar_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Área do Operador")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        status_linha = QHBoxLayout()
        self.mobile_status_label = QLabel("📱 celular: inválido")
        self.host_status_label = QLabel("🖥 host: inválido")
        status_linha.addWidget(self.mobile_status_label)
        status_linha.addWidget(self.host_status_label)
        status_linha.addStretch()
        layout.addLayout(status_linha)

        subtitulo = QLabel(f"Olá, {self.usuario.nome}. Selecione a ação desejada.")
        subtitulo.setObjectName("subtitulo")
        layout.addWidget(subtitulo)


        botoes = QGridLayout()
        self.scanner_btn = QPushButton("Busca de Caixa")
        self.dash_btn = QPushButton("Dashboard")
        self.codigos_btn = QPushButton("Códigos de Barras")

        self.scanner_btn.clicked.connect(self.abrir_scanner)
        self.dash_btn.clicked.connect(self.abrir_dashboard)
        self.codigos_btn.clicked.connect(self.abrir_codigos)

        botoes.addWidget(self.scanner_btn, 0, 0)
        botoes.addWidget(self.dash_btn, 0, 1)
        botoes.addWidget(self.codigos_btn, 1, 0)

        layout.addLayout(botoes)
        self.setLayout(layout)

    def closeEvent(self, event):
        self.mobile_request_service.parar()
       
        super().closeEvent(event)

    def _processar_codigo(self, codigo: str):
        session = get_session()
        try:
            resultado = self.scan_service.buscar_caixa_por_codigo(session, codigo)
            if not resultado["ok"]:
                return
            beep_scan()
            CaixaDetalhesDialog(resultado["caixa"], self).exec()
        finally:
            session.close()


    def _monitorar(self):
        status_mobile = self.mobile_usb_service.status_conexao().conectado
        self.mobile_status_label.setText(f"📱 celular: {'🟢 conectado' if status_mobile else '🔴 inválido'}")

        status_host = self.mobile_request_service.status().ativo
        self.host_status_label.setText(f"🖥 host: {'🟢 conectado' if status_host else '🔴 inválido'}")

        codigo_request = self.mobile_request_service.ler_codigo()
        if codigo_request:
            self._processar_codigo(codigo_request)
            return

        codigo_usb = self.mobile_usb_service.ler_codigo_usb()
        if codigo_usb:
            self._processar_codigo(codigo_usb)

    def abrir_scanner(self):
        self.w_scanner = ScannerWindow()
        self.w_scanner.show()

    def abrir_dashboard(self):
        self.w_dash = DashboardWindow()
        self.w_dash.show()


    def abrir_codigos(self):
        self.w_codigos = CodigosBarrasWindow()
        self.w_codigos.show()
