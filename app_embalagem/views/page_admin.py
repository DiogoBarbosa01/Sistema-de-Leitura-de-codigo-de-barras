from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.services.mobile_request_service import MobileRequestService
from app_embalagem.services.mobile_usb_service import MobileUsbService
from app_embalagem.services.scan_service import ScanService
from app_embalagem.utils.helpers import formatar_data_hora
from app_embalagem.utils.sound import beep_scan
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.caixa_detalhes_dialog import CaixaDetalhesDialog
from app_embalagem.views.cadastro_caixa_window import CadastroCaixaWindow
from app_embalagem.views.cadastro_funcionario_window import CadastroFuncionarioWindow
from app_embalagem.views.codigos_barras_window import CodigosBarrasWindow
from app_embalagem.views.dashboard_window import DashboardWindow
from app_embalagem.views.scanner_window import ScannerWindow
from app_embalagem.views.shadow_scan_box import ShadowScanBox


class PageAdmin(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.caixa_service = CaixaService()
        self.scan_service = ScanService()
        self.mobile_usb_service = MobileUsbService()
        self.mobile_request_service = MobileRequestService()
        self.shadow_scan_box = ShadowScanBox(self)

        self.setWindowTitle(f"Página Admin - {usuario.nome}")
        self.resize(1200, 700)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self._atualizar_tabela_caixas()
        self.shadow_scan_box.codigo_detectado.connect(self._processar_codigo)
        self.shadow_scan_box.iniciar()

        try:
            self.mobile_request_service.iniciar()
        except Exception:
            pass

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._monitorar)
        self.timer.start(1200)

        self.tabela_timer = QTimer(self)
        self.tabela_timer.timeout.connect(self._atualizar_tabela_caixas)
        self.tabela_timer.start(6000)

    def _montar_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Área de Administrador")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        status_linha = QHBoxLayout()
        self.mobile_status_label = QLabel("📱 celular: inválido")
        self.host_status_label = QLabel("🖥 host: inválido")
        status_linha.addWidget(self.mobile_status_label)
        status_linha.addWidget(self.host_status_label)
        status_linha.addStretch()
        layout.addLayout(status_linha)

        subtitulo = QLabel(f"Bem-vindo, {self.usuario.nome}. Gerencie a operação em tempo real.")
        subtitulo.setObjectName("subtitulo")
        layout.addWidget(subtitulo)


        botoes = QGridLayout()
        self.scanner_btn = QPushButton("Busca de Caixa")
        self.func_btn = QPushButton("Cadastro de Funcionário")
        self.caixa_btn = QPushButton("Cadastro de Caixa")
        self.codigos_btn = QPushButton("Códigos de Barras")
        self.dash_btn = QPushButton("Dashboard")

        self.scanner_btn.clicked.connect(self.abrir_scanner)
        self.func_btn.clicked.connect(self.abrir_funcionarios)
        self.caixa_btn.clicked.connect(self.abrir_caixas)
        self.codigos_btn.clicked.connect(self.abrir_codigos)
        self.dash_btn.clicked.connect(self.abrir_dashboard)

        botoes.addWidget(self.scanner_btn, 0, 0)
        botoes.addWidget(self.func_btn, 0, 1)
        botoes.addWidget(self.caixa_btn, 1, 0)
        botoes.addWidget(self.codigos_btn, 1, 1)
        botoes.addWidget(self.dash_btn, 2, 0)
        layout.addLayout(botoes)

        table_hint = QLabel("Cadastros de caixas (tempo real) com todos os campos informados no cadastro")
        table_hint.setObjectName("tableHint")
        layout.addWidget(table_hint)

        self.caixas_table = QTableWidget(0, 8)
        self.caixas_table.setHorizontalHeaderLabels(
            ["Código", "Nº Pedido", "Artigo", "Cor", "Emendas", "Metros", "Funcionário", "Criada em"]
        )
        self.caixas_table.verticalHeader().setVisible(False)
        self.caixas_table.setAlternatingRowColors(True)
        layout.addWidget(self.caixas_table)

        self.setLayout(layout)

    def closeEvent(self, event):
        self.mobile_request_service.parar()
        self.shadow_scan_box.parar()
        super().closeEvent(event)

    def _abrir_detalhes(self, caixa):
        CaixaDetalhesDialog(caixa, self).exec()

    def _processar_codigo(self, codigo: str):
        session = get_session()
        try:
            resultado = self.scan_service.buscar_caixa_por_codigo(session, codigo)
            if not resultado["ok"]:
                return
            beep_scan()
            self._abrir_detalhes(resultado["caixa"])
        finally:
            session.close()


    def _monitorar(self):
        self._atualizar_statuses()

        codigo_request = self.mobile_request_service.ler_codigo()
        if codigo_request:
            self._processar_codigo(codigo_request)
            return

        codigo_usb = self.mobile_usb_service.ler_codigo_usb()
        if codigo_usb:
            self._processar_codigo(codigo_usb)

    def _atualizar_statuses(self):
        status_mobile = self.mobile_usb_service.status_conexao().conectado
        dot_mobile = "🟢" if status_mobile else "🔴"
        txt_mobile = "conectado" if status_mobile else "inválido"
        self.mobile_status_label.setText(f"📱 celular: {dot_mobile} {txt_mobile}")

        status_host = self.mobile_request_service.status().ativo
        dot_host = "🟢" if status_host else "🔴"
        txt_host = "conectado" if status_host else "inválido"
        self.host_status_label.setText(f"🖥 host: {dot_host} {txt_host}")

    def _atualizar_tabela_caixas(self):
        session = get_session()
        try:
            caixas = self.caixa_service.listar_recentes(session, limite=40)
            self.caixas_table.setRowCount(len(caixas))
            for i, caixa in enumerate(caixas):
                self.caixas_table.setItem(i, 0, QTableWidgetItem(caixa.codigo_caixa))
                self.caixas_table.setItem(i, 1, QTableWidgetItem(caixa.arte))
                self.caixas_table.setItem(i, 2, QTableWidgetItem(caixa.artigo))
                self.caixas_table.setItem(i, 3, QTableWidgetItem(caixa.cor))
                self.caixas_table.setItem(i, 4, QTableWidgetItem(str(caixa.emendas)))
                self.caixas_table.setItem(i, 5, QTableWidgetItem(f"{caixa.metros:.2f}"))
                self.caixas_table.setItem(i, 6, QTableWidgetItem(caixa.nome_funcionario))
                self.caixas_table.setItem(i, 7, QTableWidgetItem(formatar_data_hora(caixa.data_criacao)))
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

    def abrir_codigos(self):
        self.w_codigos = CodigosBarrasWindow()
        self.w_codigos.show()

    def abrir_dashboard(self):
        self.w_dash = DashboardWindow()
        self.w_dash.show()

