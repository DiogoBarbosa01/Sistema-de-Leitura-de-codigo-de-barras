from pathlib import Path

from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem, QSplitter, QVBoxLayout, QWidget

from app_embalagem.config import BARCODES_DIR
from app_embalagem.utils.theme import APP_STYLESHEET


class CodigosBarrasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Códigos de Barras")
        self.resize(760, 420)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self._carregar_pastas()

    def _montar_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Códigos de Barras")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        splitter = QSplitter()
        self.pastas_list = QListWidget()
        self.arquivos_list = QListWidget()
        self.pastas_list.currentItemChanged.connect(self._carregar_arquivos_da_pasta)

        splitter.addWidget(self.pastas_list)
        splitter.addWidget(self.arquivos_list)
        splitter.setSizes([250, 500])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _carregar_pastas(self):
        self.pastas_list.clear()
        base = Path(BARCODES_DIR)
        pastas = sorted([p for p in base.iterdir() if p.is_dir()]) if base.exists() else []
        for pasta in pastas:
            item = QListWidgetItem(pasta.name)
            item.setData(32, str(pasta))
            self.pastas_list.addItem(item)

    def _carregar_arquivos_da_pasta(self, item_atual, _item_antigo):
        self.arquivos_list.clear()
        if not item_atual:
            return

        pasta = Path(item_atual.data(32))
        arquivos = sorted(pasta.glob("*.png"))
        for arquivo in arquivos:
            self.arquivos_list.addItem(arquivo.name)
