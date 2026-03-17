from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QPushButton, QSplitter, QVBoxLayout, QWidget
from sqlalchemy import select

from app_embalagem.config import BARCODES_DIR
from app_embalagem.database.connection import get_session
from app_embalagem.models.caixa import Caixa
from app_embalagem.utils.theme import APP_STYLESHEET


class CodigosBarrasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Códigos de Barras")
        self.resize(920, 520)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self._carregar_pastas()

    def _montar_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Códigos de Barras")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        self.status_label = QLabel("Pastas por Nº do pedido")
        layout.addWidget(self.status_label)

        atualizar_btn = QPushButton("Atualizar pastas")
        atualizar_btn.clicked.connect(self._carregar_pastas)
        layout.addWidget(atualizar_btn)

        splitter = QSplitter()
        listas_splitter = QSplitter(Qt.Vertical)

        self.pastas_list = QListWidget()
        self.arquivos_list = QListWidget()
        self.pastas_list.currentItemChanged.connect(self._carregar_arquivos_da_pasta)
        self.arquivos_list.currentItemChanged.connect(self._mostrar_preview_codigo)

        listas_splitter.addWidget(self.pastas_list)
        listas_splitter.addWidget(self.arquivos_list)
        listas_splitter.setSizes([200, 220])

        self.preview_label = QLabel("Selecione um código de barras para visualizar a imagem.")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border:1px solid #3a3a3a; border-radius:8px; padding:8px; min-height:320px;")

        splitter.addWidget(listas_splitter)
        splitter.addWidget(self.preview_label)
        splitter.setSizes([320, 600])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _organizar_arquivos_legados(self):
        """Move PNGs antigos da raiz para pasta do número do pedido, quando possível."""
        base = Path(BARCODES_DIR)
        arquivos_soltos = list(base.glob("*.png"))
        if not arquivos_soltos:
            return

        session = get_session()
        try:
            for arquivo in arquivos_soltos:
                codigo = arquivo.stem
                caixa = session.scalar(select(Caixa).where(Caixa.codigo_caixa == codigo))
                if not caixa:
                    continue
                pasta_destino = base / str(caixa.arte)
                pasta_destino.mkdir(parents=True, exist_ok=True)
                destino = pasta_destino / arquivo.name
                if not destino.exists():
                    arquivo.replace(destino)
        finally:
            session.close()

    def _carregar_pastas(self):
        self._organizar_arquivos_legados()
        self.pastas_list.clear()
        self.arquivos_list.clear()
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Selecione um código de barras para visualizar a imagem.")

        base = Path(BARCODES_DIR)
        pastas = sorted([p for p in base.iterdir() if p.is_dir()]) if base.exists() else []

        if not pastas:
            self.status_label.setText(
                "Nenhuma pasta encontrada. Gere uma etiqueta para criar pastas por Nº do pedido (ex.: 1000)."
            )
            return

        for pasta in pastas:
            qtd_png = len(list(pasta.glob("*.png")))
            item = QListWidgetItem(f"{pasta.name} ({qtd_png})")
            item.setData(32, str(pasta))
            self.pastas_list.addItem(item)

        self.status_label.setText(f"{len(pastas)} pasta(s) encontrada(s).")
        self.pastas_list.setCurrentRow(0)

    def _carregar_arquivos_da_pasta(self, item_atual, _item_antigo):
        self.arquivos_list.clear()
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Selecione um código de barras para visualizar a imagem.")
        if not item_atual:
            return

        pasta = Path(item_atual.data(32))
        arquivos = sorted(pasta.glob("*.png"))
        if not arquivos:
            self.arquivos_list.addItem("(Sem códigos PNG nesta pasta)")
            return

        for arquivo in arquivos:
            item = QListWidgetItem(arquivo.name)
            item.setData(32, str(arquivo))
            self.arquivos_list.addItem(item)

        self.arquivos_list.setCurrentRow(0)

    def _mostrar_preview_codigo(self, item_atual, _item_antigo):
        if not item_atual:
            return

        caminho = item_atual.data(32)
        if not caminho:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Sem imagem disponível para este item.")
            return

        pixmap = QPixmap(caminho)
        if pixmap.isNull():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Não foi possível carregar a imagem do código de barras.")
            return

        self.preview_label.setPixmap(pixmap.scaled(560, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation))
