from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select

from app_embalagem.config import BARCODES_DIR
from app_embalagem.database.connection import get_session
from app_embalagem.models.caixa import Caixa
from app_embalagem.utils.theme import APP_STYLESHEET


class CodigosBarrasWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Códigos de Barras")
        self.resize(980, 560)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self._carregar_explorador()

    def _montar_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Códigos de Barras")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        self.status_label = QLabel("Explorador de arquivos das etiquetas")
        self.status_label.setObjectName("subtitulo")
        layout.addWidget(self.status_label)

        atualizar_btn = QPushButton("Atualizar")
        atualizar_btn.clicked.connect(self._carregar_explorador)
        layout.addWidget(atualizar_btn)

        splitter = QSplitter()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nome", "Tipo"])
        self.tree.itemSelectionChanged.connect(self._mostrar_preview_selecionado)

        self.preview_label = QLabel("Selecione uma etiqueta (.png) para visualizar.")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setObjectName("card")
        self.preview_label.setMinimumHeight(340)

        splitter.addWidget(self.tree)
        splitter.addWidget(self.preview_label)
        splitter.setSizes([420, 560])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _organizar_arquivos_legados(self):
        base = Path(BARCODES_DIR)
        arquivos_soltos = list(base.glob("*.png"))
        if not arquivos_soltos:
            return

        session = get_session()
        try:
            for arquivo in arquivos_soltos:
                caixa = session.scalar(select(Caixa).where(Caixa.codigo_caixa == arquivo.stem))
                if not caixa:
                    continue
                pasta_destino = base / str(caixa.arte)
                pasta_destino.mkdir(parents=True, exist_ok=True)
                destino = pasta_destino / arquivo.name
                if not destino.exists():
                    arquivo.replace(destino)
        finally:
            session.close()

    def _carregar_explorador(self):
        self._organizar_arquivos_legados()
        self.tree.clear()
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Selecione uma etiqueta (.png) para visualizar.")

        base = Path(BARCODES_DIR)
        if not base.exists():
            self.status_label.setText("Pasta de códigos não encontrada.")
            return

        pastas = sorted([p for p in base.iterdir() if p.is_dir()])
        if not pastas:
            self.status_label.setText("Nenhuma pasta encontrada. Gere uma etiqueta para popular o explorador.")
            return

        total_arquivos = 0
        for pasta in pastas:
            pasta_item = QTreeWidgetItem([pasta.name, "Pasta"])
            pasta_item.setData(0, Qt.UserRole, str(pasta))
            pasta_item.setData(1, Qt.UserRole, "folder")
            pasta_item.setIcon(0, self.style().standardIcon(self.style().SP_DirIcon))

            for arquivo in sorted(pasta.glob("*.png")):
                total_arquivos += 1
                file_item = QTreeWidgetItem([arquivo.name, "Arquivo PNG"])
                file_item.setData(0, Qt.UserRole, str(arquivo))
                file_item.setData(1, Qt.UserRole, "file")
                file_item.setIcon(0, self.style().standardIcon(self.style().SP_FileIcon))
                pasta_item.addChild(file_item)

            self.tree.addTopLevelItem(pasta_item)
            pasta_item.setExpanded(True)

        self.status_label.setText(f"{len(pastas)} pasta(s) e {total_arquivos} arquivo(s) carregados.")

    def _mostrar_preview_selecionado(self):
        itens = self.tree.selectedItems()
        if not itens:
            return

        item = itens[0]
        if item.data(1, Qt.UserRole) != "file":
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Selecione um arquivo PNG para visualizar.")
            return

        caminho = item.data(0, Qt.UserRole)
        pixmap = QPixmap(caminho)
        if pixmap.isNull():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Não foi possível carregar a imagem selecionada.")
            return

        self.preview_label.setPixmap(pixmap.scaled(560, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation))
