from datetime import timezone

from PySide6.QtWidgets import QDialog, QFormLayout, QLabel, QVBoxLayout

from app_embalagem.utils.theme import APP_STYLESHEET

from app_embalagem.utils.helpers import formatar_data_hora



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

            
    
      
            

        form = QFormLayout()
        form.addRow("Código de barras:", QLabel(self.caixa.codigo_caixa))
        form.addRow("Número do pedido:", QLabel(self.caixa.arte))
        form.addRow("Funcionário:", QLabel(getattr(self.caixa, "nome_funcionario", self.caixa.sigla_funcionario)))
        form.addRow("Artigo:", QLabel(self.caixa.artigo))
        form.addRow("Cor:", QLabel(getattr(self.caixa, "cor", "-")))
        form.addRow("Emendas:", QLabel(str(getattr(self.caixa, "emendas", 0))))
        form.addRow("Metros:", QLabel(f"{self.caixa.metros:.2f}"))        
        form.addRow("Data/Hora:",QLabel(f"{formatar_data_hora(self.caixa.data_criacao)}")
)

        
        layout.addLayout(form)
        self.setLayout(layout)

    