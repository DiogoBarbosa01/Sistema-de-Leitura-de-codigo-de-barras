from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QVBoxLayout

from app_embalagem.utils.theme import APP_STYLESHEET


class CaixaDetalhesDialog(QDialog):
    def __init__(self, caixa, parent=None):
        super().__init__(parent)
        self.caixa = caixa
        self.setWindowTitle("Janela de dados")
        self.resize(500, 300)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _montar_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Janela de dados da caixa")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        data_registro = self.caixa.data_criacao.strftime("%d/%m/%Y")
        hora_registro = self.caixa.data_criacao.strftime("%H:%M:%S")

        form = QFormLayout()
        form.addRow("Código de barras:", QLabel(self.caixa.codigo_caixa))
        form.addRow("Número do pedido:", QLabel(self.caixa.arte))
        form.addRow("Funcionário:", QLabel(self.caixa.sigla_funcionario))
        form.addRow("Metros:", QLabel(f"{self.caixa.metros:.2f}"))
        form.addRow("Dia registrado:", QLabel(data_registro))
        form.addRow("Hora registrada:", QLabel(hora_registro))

        layout.addLayout(form)
        self.setLayout(layout)
