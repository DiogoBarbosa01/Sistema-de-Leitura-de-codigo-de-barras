from pathlib import Path

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
        self.resize(820, 460)
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
        self.pastas_list = QListWidget()
        self.arquivos_list = QListWidget()
        self.pastas_list.currentItemChanged.connect(self._carregar_arquivos_da_pasta)

        splitter.addWidget(self.pastas_list)
        splitter.addWidget(self.arquivos_list)
        splitter.setSizes([280, 540])

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
        if not item_atual:
            return

        pasta = Path(item_atual.data(32))
        arquivos = sorted(pasta.glob("*.png"))
        if not arquivos:
            self.arquivos_list.addItem("(Sem códigos PNG nesta pasta)")
            return

        for arquivo in arquivos:
            self.arquivos_list.addItem(arquivo.name)
