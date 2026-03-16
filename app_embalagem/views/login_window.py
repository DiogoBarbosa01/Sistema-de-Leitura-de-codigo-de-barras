from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app_embalagem.database.connection import get_session
from app_embalagem.services.auth_service import AuthService
from app_embalagem.views.cadastro_usuario_window import CadastroUsuarioWindow
from app_embalagem.views.page_admin import PageAdmin
from app_embalagem.views.page_operador import PageOperador


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.setWindowTitle("Login - Controle de Embalagem")
        self._montar_ui()
        self._garantir_admin_padrao()

    def _montar_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Faça login para continuar"))

        form = QFormLayout()
        self.username_input = QLineEdit()
        self.senha_input = QLineEdit()
        self.senha_input.setEchoMode(QLineEdit.Password)
        form.addRow("Usuário:", self.username_input)
        form.addRow("Senha:", self.senha_input)
        layout.addLayout(form)

        botoes = QHBoxLayout()
        entrar_btn = QPushButton("Entrar")
        entrar_btn.clicked.connect(self._fazer_login)

        cadastro_btn = QPushButton("Cadastrar usuário")
        cadastro_btn.clicked.connect(self._abrir_cadastro_usuario)

        botoes.addWidget(entrar_btn)
        botoes.addWidget(cadastro_btn)
        layout.addLayout(botoes)
        self.setLayout(layout)

    def _garantir_admin_padrao(self):
        session = get_session()
        try:
            self.auth_service.criar_usuario_inicial(session)
        finally:
            session.close()

    def _abrir_cadastro_usuario(self):
        self.w_cadastro_usuario = CadastroUsuarioWindow()
        self.w_cadastro_usuario.show()

    def _fazer_login(self):
        session = get_session()
        try:
            usuario = self.auth_service.autenticar(session, self.username_input.text().strip(), self.senha_input.text())
            if not usuario:
                QMessageBox.warning(self, "Falha", "Usuário/senha inválidos ou usuário inativo.")
                return

            if usuario.perfil == "admin":
                self.main_window = PageAdmin(usuario)
            else:
                self.main_window = PageOperador(usuario)

            self.main_window.show()
            self.close()
        finally:
            session.close()
