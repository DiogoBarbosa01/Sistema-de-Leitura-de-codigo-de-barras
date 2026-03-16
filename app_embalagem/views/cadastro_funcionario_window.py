from PySide6.QtWidgets import QCheckBox, QFormLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.funcionario_service import FuncionarioService
from app_embalagem.utils.validators import validar_texto_obrigatorio


class CadastroFuncionarioWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.service = FuncionarioService()
        self.setWindowTitle("Cadastro de Funcionário")
        self._montar_ui()

    def _montar_ui(self):
        layout = QVBoxLayout()
        form = QFormLayout()

        from PySide6.QtWidgets import QLineEdit

        self.nome_input = QLineEdit()
        self.matricula_input = QLineEdit()
        self.ativo_check = QCheckBox("Ativo")
        self.ativo_check.setChecked(True)

        form.addRow("Nome:", self.nome_input)
        form.addRow("Matrícula:", self.matricula_input)
        form.addRow("Status:", self.ativo_check)

        salvar_btn = QPushButton("Salvar")
        salvar_btn.clicked.connect(self._salvar)

        layout.addLayout(form)
        layout.addWidget(salvar_btn)
        self.setLayout(layout)

    def _salvar(self):
        erro_nome = validar_texto_obrigatorio(self.nome_input.text(), "nome")
        erro_matricula = validar_texto_obrigatorio(self.matricula_input.text(), "matrícula")
        if erro_nome or erro_matricula:
            QMessageBox.warning(self, "Validação", erro_nome or erro_matricula)
            return

        session = get_session()
        try:
            funcionario = self.service.criar_funcionario(
                session,
                nome=self.nome_input.text().strip(),
                matricula=self.matricula_input.text().strip(),
                ativo=self.ativo_check.isChecked(),
            )
            QMessageBox.information(
                self,
                "Sucesso",
                f"Funcionário criado com sucesso. Código: {funcionario.codigo_barras}",
            )
            self.nome_input.clear()
            self.matricula_input.clear()
            self.ativo_check.setChecked(True)
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Falha ao salvar funcionário: {exc}")
        finally:
            session.close()
