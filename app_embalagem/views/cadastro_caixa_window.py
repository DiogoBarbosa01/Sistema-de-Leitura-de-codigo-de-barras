from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app_embalagem.database.connection import get_session
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.services.funcionario_service import FuncionarioService
from app_embalagem.utils.validators import validar_metros, validar_texto_obrigatorio


class CadastroCaixaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.caixa_service = CaixaService()
        self.funcionario_service = FuncionarioService()
        self.ultimo_arquivo = ""
        self.setWindowTitle("Cadastro de Caixa / Etiqueta")
        self._montar_ui()
        self._carregar_funcionarios()

    def _montar_ui(self):
        from PySide6.QtWidgets import QLineEdit

        layout = QVBoxLayout()
        form = QFormLayout()

        self.arte_input = QLineEdit()
        self.artigo_input = QLineEdit()
        self.metros_input = QLineEdit()
        self.funcionario_combo = QComboBox()

        form.addRow("ARTE:", self.arte_input)
        form.addRow("Artigo:", self.artigo_input)
        form.addRow("Metros:", self.metros_input)
        form.addRow("Funcionário:", self.funcionario_combo)

        self.info_label = QLabel("Arquivo de etiqueta: -")

        self.gerar_btn = QPushButton("Gerar etiqueta")
        self.gerar_btn.clicked.connect(self._gerar_etiqueta)

        self.preview_label = QLabel("Pré-visualização da etiqueta")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border:1px solid #3a3a3a; border-radius:8px; padding:10px; min-height:120px;")

        self.imprimir_btn = QPushButton("Imprimir")
        self.imprimir_btn.clicked.connect(self._imprimir_etiqueta)
        self.imprimir_btn.setEnabled(False)

        botoes_layout = QHBoxLayout()
        botoes_layout.addWidget(self.gerar_btn)
        botoes_layout.addWidget(self.imprimir_btn)

        layout.addLayout(form)
        layout.addLayout(botoes_layout)
        layout.addWidget(self.info_label)
        layout.addWidget(self.preview_label)
        self.setLayout(layout)

    def _carregar_funcionarios(self):
        session = get_session()
        try:
            funcionarios = self.funcionario_service.listar_todos(session)
            self.funcionario_combo.clear()
            for f in funcionarios:
                if f.ativo:
                    self.funcionario_combo.addItem(f"{f.nome} ({f.codigo_barras})", f.nome)
        finally:
            session.close()

    def _gerar_etiqueta(self):
        erro_arte = validar_texto_obrigatorio(self.arte_input.text(), "ARTE")
        erro_artigo = validar_texto_obrigatorio(self.artigo_input.text(), "artigo")
        erro_metros = validar_metros(self.metros_input.text().strip())

        if erro_arte or erro_artigo or erro_metros:
            QMessageBox.warning(self, "Validação", erro_arte or erro_artigo or erro_metros)
            return

        nome_funcionario = self.funcionario_combo.currentData()
        if not nome_funcionario:
            QMessageBox.warning(self, "Validação", "Cadastre ao menos um funcionário ativo para gerar a etiqueta.")
            return

        session = get_session()
        try:
            caixa, caminho = self.caixa_service.criar_caixa(
                session,
                arte=self.arte_input.text().strip(),
                artigo=self.artigo_input.text().strip(),
                metros=float(self.metros_input.text().strip().replace(",", ".")),
                nome_funcionario=nome_funcionario,
            )
            self.ultimo_arquivo = caminho
            self.info_label.setText(f"Arquivo de etiqueta: {caminho}")
            self._mostrar_preview(caminho)
            self.imprimir_btn.setEnabled(True)
            QMessageBox.information(self, "Sucesso", f"Etiqueta gerada para {caixa.codigo_caixa}.")
            self.arte_input.clear()
            self.artigo_input.clear()
            self.metros_input.clear()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Erro", f"Não foi possível gerar etiqueta: {exc}")
        finally:
            session.close()

    def _mostrar_preview(self, caminho: str):
        pixmap = QPixmap(caminho)
        if pixmap.isNull():
            self.preview_label.setText("Não foi possível carregar a imagem da etiqueta.")
            return
        self.preview_label.setPixmap(pixmap.scaled(420, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _imprimir_etiqueta(self):
        if not self.ultimo_arquivo:
            return

        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QPrintDialog.Accepted:
            return

        pixmap = QPixmap(self.ultimo_arquivo)
        if pixmap.isNull():
            QMessageBox.warning(self, "Impressão", "Imagem da etiqueta inválida.")
            return

        painter = None
        try:
            from PySide6.QtGui import QPainter

            painter = QPainter(printer)
            rect = painter.viewport()
            escala = pixmap.scaled(rect.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.setViewport(rect.x(), rect.y(), escala.width(), escala.height())
            painter.setWindow(pixmap.rect())
            painter.drawPixmap(0, 0, pixmap)
        finally:
            if painter:
                painter.end()
