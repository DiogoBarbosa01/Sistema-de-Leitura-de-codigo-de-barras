from PySide6.QtWidgets import QFormLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.utils.validators import validar_quantidade, validar_texto_obrigatorio


class CadastroCaixaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.service = CaixaService()
        self.ultimo_arquivo = ""
        self.setWindowTitle("Cadastro de Caixa")
        self._montar_ui()

    def _montar_ui(self):
        from PySide6.QtWidgets import QLineEdit

        layout = QVBoxLayout()
        form = QFormLayout()
        self.produto_input = QLineEdit()
        self.quantidade_input = QLineEdit()

        form.addRow("Produto:", self.produto_input)
        form.addRow("Quantidade:", self.quantidade_input)

        self.info_label = QLabel("Arquivo de etiqueta: -")

        salvar_btn = QPushButton("Salvar")
        salvar_btn.clicked.connect(self._salvar)
        gerar_btn = QPushButton("Gerar etiqueta")
        gerar_btn.clicked.connect(self._salvar)

        layout.addLayout(form)
        layout.addWidget(salvar_btn)
        layout.addWidget(gerar_btn)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def _salvar(self):
        erro_produto = validar_texto_obrigatorio(self.produto_input.text(), "produto")
        erro_qtd = validar_quantidade(self.quantidade_input.text().strip())
        if erro_produto or erro_qtd:
            QMessageBox.warning(self, "Validação", erro_produto or erro_qtd)
            return

        session = get_session()
        try:
            caixa, caminho = self.service.criar_caixa(
                session,
                produto=self.produto_input.text().strip(),
                quantidade=int(self.quantidade_input.text().strip()),
            )
            self.ultimo_arquivo = caminho
            self.info_label.setText(f"Arquivo de etiqueta: {caminho}")
            QMessageBox.information(self, "Sucesso", f"Caixa {caixa.codigo_caixa} criada.")
            self.produto_input.clear()
            self.quantidade_input.clear()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Não foi possível criar caixa: {exc}")
        finally:
            session.close()
