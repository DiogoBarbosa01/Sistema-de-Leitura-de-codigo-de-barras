from datetime import timezone

from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QVBoxLayout

from app_embalagem.utils.theme import APP_STYLESHEET


class CaixaDetalhesDialog(QDialog):
    def __init__(self, caixa, parent=None):
        super().__init__(parent)
        self.caixa = caixa
        self.setWindowTitle("Janela de dados")
        self.resize(520, 340)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _montar_ui(self):
        layout = QVBoxLayout()

        titulo = QLabel("Janela de dados da caixa")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        data_local = self._ajustar_para_horario_local(self.caixa.data_criacao)
        data_registro = data_local.strftime("%d/%m/%Y")
        hora_registro = data_local.strftime("%H:%M:%S")

        form = QFormLayout()
        form.addRow("Código de barras:", QLabel(self.caixa.codigo_caixa))
        form.addRow("Número do pedido:", QLabel(self.caixa.arte))
        form.addRow("Funcionário:", QLabel(getattr(self.caixa, "nome_funcionario", self.caixa.sigla_funcionario)))
        form.addRow("Artigo:", QLabel(self.caixa.artigo))
        form.addRow("Cor:", QLabel(getattr(self.caixa, "cor", "-")))
        form.addRow("Emendas:", QLabel(str(getattr(self.caixa, "emendas", 0))))
        form.addRow("Metros:", QLabel(f"{self.caixa.metros:.2f}"))
        form.addRow("Dia registrado:", QLabel(data_registro))
        form.addRow("Hora registrada:", QLabel(hora_registro))

        layout.addLayout(form)
        self.setLayout(layout)

    @staticmethod
    def _ajustar_para_horario_local(data_hora):
        if data_hora.tzinfo is None:
            # compatibilidade com registros antigos que estavam em UTC sem timezone.
            return data_hora.replace(tzinfo=timezone.utc).astimezone()
        return data_hora.astimezone()
