from PySide6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.usuario_service import UsuarioService
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.utils.validators import validar_texto_obrigatorio


class CadastroUsuarioWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.service = UsuarioService()
        self.setWindowTitle("Cadastro de Usuário")
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

    def _montar_ui(self):
        layout = QVBoxLayout()

        form = QFormLayout()
        self.username_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)

        self.perfil_combo = QComboBox()
        self.perfil_combo.addItems(["operador", "admin"])

        self.ativo_check = QCheckBox("Ativo")
        self.ativo_check.setChecked(True)

        form.addRow("Username:", self.username_input)
        form.addRow("Nome:", self.nome_input)
        form.addRow("Senha:", self.senha_input)
        form.addRow("Perfil:", self.perfil_combo)
        form.addRow("Status:", self.ativo_check)

        salvar_btn = QPushButton("Salvar usuário")
        salvar_btn.clicked.connect(self._salvar)

        layout.addLayout(form)
        layout.addWidget(salvar_btn)
        self.setLayout(layout)

    def _salvar(self):
        validacoes = [
            validar_texto_obrigatorio(self.username_input.text(), "username"),
            validar_texto_obrigatorio(self.nome_input.text(), "nome"),
            validar_texto_obrigatorio(self.senha_input.text(), "senha"),
        ]
        erro = next((item for item in validacoes if item), None)
        if erro:
            QMessageBox.warning(self, "Validação", erro)
            return

        session = get_session()
        try:
            usuario = self.service.criar_usuario(
                session,
                username=self.username_input.text(),
                senha=self.senha_input.text(),
                nome=self.nome_input.text(),
                perfil=self.perfil_combo.currentText(),
                ativo=self.ativo_check.isChecked(),
            )
            QMessageBox.information(self, "Sucesso", f"Usuário '{usuario.username}' criado com perfil {usuario.perfil}.")
            self.username_input.clear()
            self.nome_input.clear()
            self.senha_input.clear()
            self.perfil_combo.setCurrentText("operador")
            self.ativo_check.setChecked(True)
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Erro", str(exc))
        finally:
            session.close()
