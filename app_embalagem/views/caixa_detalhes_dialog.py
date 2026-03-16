from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QVBoxLayout

from app_embalagem.utils.helpers import formatar_data_hora
from app_embalagem.utils.theme import APP_STYLESHEET


class CaixaDetalhesDialog(QDialog):
    def __init__(self, caixa, parent=None):
        super().__init__(parent)
        self.caixa = caixa
        self.setWindowTitle("Detalhes da Caixa")
        self.resize(460, 280)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _montar_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Informações da Caixa")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        form = QFormLayout()
        form.addRow("Código:", QLabel(self.caixa.codigo_caixa))
        form.addRow("Nº pedido:", QLabel(self.caixa.arte))
        form.addRow("Artigo:", QLabel(self.caixa.artigo))
        form.addRow("Metros:", QLabel(f"{self.caixa.metros:.2f}"))
        form.addRow("Sigla funcionário:", QLabel(self.caixa.sigla_funcionario))
        form.addRow("Status:", QLabel(self.caixa.status))
        form.addRow("Criada em:", QLabel(formatar_data_hora(self.caixa.data_criacao)))

        layout.addLayout(form)
        self.setLayout(layout)
