from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.mobile_request_service import MobileRequestService
from app_embalagem.services.mobile_usb_service import MobileUsbService
from app_embalagem.services.scan_service import ScanService
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.caixa_detalhes_dialog import CaixaDetalhesDialog


class ScannerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.scan_service = ScanService()
        self.mobile_usb_service = MobileUsbService()
        self.mobile_request_service = MobileRequestService()
        self.setWindowTitle("Scanner / Filtro de Código")
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

        try:
            self.mobile_request_service.iniciar()
        except Exception as exc:
            self.mobile_req_label.setText(f"Requisição via celular: erro ao iniciar ({exc})")

        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._monitorar_entradas)
        self.monitor_timer.start(1200)

    def _montar_ui(self):
        layout = QVBoxLayout()

        self.mobile_status_label = QLabel("Status ADB: verificando...")
        layout.addWidget(self.mobile_status_label)

        self.mobile_req_label = QLabel("Requisição via celular: inicializando...")
        layout.addWidget(self.mobile_req_label)

        subtitulo = QLabel("Digite, escaneie USB ou envie pelo celular para solicitar busca da caixa")
        layout.addWidget(subtitulo)

        form = QFormLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Ex.: CX-2616CNI0001000002")
        self.scan_input.returnPressed.connect(self._processar_filtro_manual)
        form.addRow("Filtro por código:", self.scan_input)
        layout.addLayout(form)

        self.buscar_btn = QPushButton("Buscar caixa")
        self.buscar_btn.clicked.connect(self._processar_filtro_manual)
        layout.addWidget(self.buscar_btn)

        self.setLayout(layout)
        QTimer.singleShot(50, self.scan_input.setFocus)

    def closeEvent(self, event):
        self.mobile_request_service.parar()
        super().closeEvent(event)

    def _abrir_detalhes_caixa(self, caixa):
        dlg = CaixaDetalhesDialog(caixa, self)
        dlg.exec()

    def _processar_codigo(self, codigo: str, limpar_input: bool = False):
        session = get_session()
        try:
            resultado = self.scan_service.buscar_caixa_por_codigo(session, codigo)
            if not resultado["ok"]:
                QMessageBox.warning(self, "Aviso", resultado["mensagem"])
                return
            self._abrir_detalhes_caixa(resultado["caixa"])
        finally:
            session.close()
            if limpar_input:
                self.scan_input.clear()
                self.scan_input.setFocus()

    def _processar_filtro_manual(self):
        codigo = self.scan_input.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Validação", "Informe um código de barras para filtrar.")
            return
        self._processar_codigo(codigo, limpar_input=True)


    def _confirmar_e_processar_codigo_celular(self, codigo: str):
        resposta = QMessageBox.question(
            self,
            "Leitura de código recebida",
            f"Leitura de código a ser realizada:\n\n{codigo}\n\nDeseja confirmar a busca desta caixa?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if resposta != QMessageBox.Yes:
            return
        self._processar_codigo(codigo)

    def _monitorar_entradas(self):
        self._atualizar_statuses()

        codigo_request = self.mobile_request_service.ler_codigo()
        if codigo_request:
            self._confirmar_e_processar_codigo_celular(codigo_request)
            return

        codigo_usb = self.mobile_usb_service.ler_codigo_usb()
        if codigo_usb:
            self._processar_codigo(codigo_usb)

    def _atualizar_statuses(self):
        status = self.mobile_usb_service.status_conexao()
        if status.conectado:
            self.mobile_status_label.setText(f"Status ADB: <b style='color:#52d66a'>Conectado</b> - {status.mensagem}")
        else:
            self.mobile_status_label.setText(f"Status ADB: <b style='color:#ff5b5b'>Inválido</b> - {status.mensagem}")

        req_status = self.mobile_request_service.status()
        if req_status.ativo:
            self.mobile_req_label.setText(
                f"Requisição via celular: <b style='color:#52d66a'>Ativa</b> - {req_status.mensagem}"
            )
        else:
            self.mobile_req_label.setText(
                f"Requisição via celular: <b style='color:#ff5b5b'>Inativa</b> - {req_status.mensagem}"
            )
