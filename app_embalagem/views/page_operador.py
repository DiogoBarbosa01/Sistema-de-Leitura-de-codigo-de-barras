from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget
from app_embalagem.database.connection import get_session
from app_embalagem.services.mobile_request_service import MobileRequestService
from app_embalagem.services.mobile_usb_service import MobileUsbService
from app_embalagem.services.scan_service import ScanService
from app_embalagem.utils.sound import beep_scan
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.caixa_detalhes_dialog import CaixaDetalhesDialog
from app_embalagem.views.cadastro_caixa_window import CadastroCaixaWindow
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
        self.resize(1280, 760)
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
        layout = QHBoxLayout()

        sidebar = QFrame()
        sidebar.setObjectName("opSidebar")
        side_layout = QVBoxLayout(sidebar)
        brand = QLabel("AnicornApp")
        brand.setObjectName("opBrand")
        side_layout.addWidget(brand)
        menu = QListWidget()
        for item in ["Dashboard", "Pedidos", "Rastreamento", "Receita", "Analytics", "Config", "Sair"]:
            QListWidgetItem(item, menu)
        menu.setCurrentRow(0)
        side_layout.addWidget(menu)

        center = QVBoxLayout()
        header = QHBoxLayout()
        titulo = QLabel("Analytics overview")
        titulo.setObjectName("tituloDashboard")
        header.addWidget(titulo)
        header.addStretch()
        search = QLabel("search...")
        search.setObjectName("textoAux")
        header.addWidget(search)
        center.addLayout(header)

        status_linha = QHBoxLayout()
        self.mobile_status_label = QLabel("📱 celular: inválido")
        self.host_status_label = QLabel("🖥 host: inválido")
        status_linha.addWidget(self.mobile_status_label)
        status_linha.addWidget(self.host_status_label)
        status_linha.addStretch()
        center.addLayout(status_linha)

        subtitulo = QLabel(f"Olá, {self.usuario.nome}. Selecione a ação desejada.")
        subtitulo.setObjectName("subtitulo")
        center.addWidget(subtitulo)

        botoes = QGridLayout()
        self.scanner_btn = QPushButton("Busca de Caixa")
        self.cadastro_caixa_btn = QPushButton("Cadastro de Caixa")
        self.dash_btn = QPushButton("Dashboard")
        self.codigos_btn = QPushButton("Códigos de Barras")

        self.scanner_btn.clicked.connect(self.abrir_scanner)
        self.cadastro_caixa_btn.clicked.connect(self.abrir_cadastro_caixa)
        self.dash_btn.clicked.connect(self.abrir_dashboard)
        self.codigos_btn.clicked.connect(self.abrir_codigos)

        botoes.addWidget(self.scanner_btn, 0, 0)
        botoes.addWidget(self.dash_btn, 0, 1)
        botoes.addWidget(self.cadastro_caixa_btn, 1, 0)
        botoes.addWidget(self.codigos_btn, 1, 1)
        center.addLayout(botoes)

        profile = QFrame()
        profile.setObjectName("opProfile")
        profile_layout = QVBoxLayout(profile)
        profile_layout.addWidget(QLabel("Profile"))
        card = QFrame()
        card.setObjectName("opProfileCard")
        card_layout = QVBoxLayout(card)
        name = QLabel(self.usuario.nome)
        name.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(name)
        card_layout.addWidget(QLabel("Operador"), alignment=Qt.AlignCenter)
        profile_layout.addWidget(card)
        profile_layout.addWidget(QLabel("Notification"))
        profile_layout.addWidget(QLabel("• Conexão host monitorada"))
        profile_layout.addWidget(QLabel("• Scanner pronto"))
        profile_layout.addStretch()

        layout.addWidget(sidebar, 2)
        layout.addLayout(center, 7)
        layout.addWidget(profile, 3)
        self.setLayout(layout)
        self.setStyleSheet(APP_STYLESHEET + """
            QFrame#opSidebar { background:#6D28D9; border-radius:18px; color:white; }
            QLabel#opBrand { color:white; font-size:24px; font-weight:700; padding:10px; }
            QListWidget { background:transparent; border:none; color:white; }
            QListWidget::item { padding:10px; border-radius:10px; margin:2px 0; }
            QListWidget::item:selected { background:#fb7185; color:white; }
            QFrame#opProfile { background:#ffffff; border-radius:18px; padding:10px; }
            QFrame#opProfileCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #FDBA74, stop:1 #FB7185); border-radius:14px; min-height:180px; }
        """)

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

    def abrir_cadastro_caixa(self):
        self.w_cadastro_caixa = CadastroCaixaWindow()
        self.w_cadastro_caixa.show()

    def abrir_dashboard(self):
        self.w_dash = DashboardWindow()
        self.w_dash.show()


    def abrir_codigos(self):
        self.w_codigos = CodigosBarrasWindow()
        self.w_codigos.show()
