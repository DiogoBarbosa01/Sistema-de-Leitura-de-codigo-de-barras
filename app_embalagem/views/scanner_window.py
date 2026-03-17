from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.scan_service import ScanService
from app_embalagem.utils.sound import beep_scan
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.caixa_detalhes_dialog import CaixaDetalhesDialog


class ScannerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.scan_service = ScanService()
        self.setWindowTitle("Busca de Caixa")
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _montar_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Busca de Caixa")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        subtitulo = QLabel("Use esta aba para filtrar e localizar caixas por código")
        subtitulo.setObjectName("subtitulo")
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
            beep_scan()
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
