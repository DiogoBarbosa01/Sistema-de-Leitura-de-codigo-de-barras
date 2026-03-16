from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app_embalagem.database.connection import get_session
from app_embalagem.services.scan_service import ScanService


class ScannerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.scan_service = ScanService()
        self.funcionario_atual = None
        self.setWindowTitle("Scanner USB / Celular")
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout()
        self.status_label = QLabel("Funcionário atual: nenhum")
        layout.addWidget(self.status_label)

        form = QFormLayout()
        self.scan_input = QLineEdit()
        self.scan_input.setPlaceholderText("Escaneie aqui com scanner USB")
        self.scan_input.returnPressed.connect(self._processar_usb)

        self.mobile_input = QLineEdit()
        self.mobile_input.setPlaceholderText("Cole ou digite o código lido pelo celular")

        form.addRow("Scanner USB:", self.scan_input)
        form.addRow("Leitura por celular:", self.mobile_input)
        layout.addLayout(form)

        self.mobile_btn = QPushButton("Registrar leitura de celular")
        self.mobile_btn.clicked.connect(self._processar_celular)
        layout.addWidget(self.mobile_btn)

        self.setLayout(layout)
        QTimer.singleShot(50, self.scan_input.setFocus)

    def _aplicar_resultado(self, resultado):
        if not resultado["ok"]:
            QMessageBox.warning(self, "Aviso", resultado["mensagem"])
            return

        if resultado.get("tipo") == "funcionario":
            self.funcionario_atual = resultado["funcionario"]
            self.status_label.setText(f"Funcionário atual: {self.funcionario_atual.nome}")
        else:
            QMessageBox.information(self, "Sucesso", resultado["mensagem"])

    def _processar_usb(self):
        codigo = self.scan_input.text().strip()
        if not codigo:
            return
        session = get_session()
        try:
            resultado = self.scan_service.processar_scan(session, codigo, self.funcionario_atual, origem="usb")
            self._aplicar_resultado(resultado)
        finally:
            session.close()
            self.scan_input.clear()
            self.scan_input.setFocus()

    def _processar_celular(self):
        codigo = self.mobile_input.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Validação", "Informe um código no campo de celular.")
            return
        session = get_session()
        try:
            resultado = self.scan_service.processar_scan_celular(session, codigo, self.funcionario_atual)
            self._aplicar_resultado(resultado)
        finally:
            session.close()
            self.mobile_input.clear()
            self.scan_input.setFocus()
