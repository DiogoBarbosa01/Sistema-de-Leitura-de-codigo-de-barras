from pathlib import Path

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStyle,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from app_embalagem.config import BARCODES_DIR
from app_embalagem.database.connection import get_session
from app_embalagem.models.caixa import Caixa
from app_embalagem.utils.theme import APP_STYLESHEET


class CodigosBarrasWindow(QWidget):
    def __init__(self, filtro_inicial: str = ""):
        super().__init__()
        self.pasta_atual: Path | None = None
        self.arquivos_da_pasta: list[Path] = []
        self.setWindowTitle("Códigos de Barras")
        self.resize(1180, 650)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        if filtro_inicial:
            self.filtro_input.setText(filtro_inicial)
        self._carregar_explorador()

    def _montar_ui(self):
        layout = QVBoxLayout()
        titulo = QLabel("Códigos de Barras")
        titulo.setObjectName("tituloPagina")
        layout.addWidget(titulo)

        self.status_label = QLabel("Explorador de etiquetas")
        self.status_label.setObjectName("subtitulo")
        layout.addWidget(self.status_label)

        filtro_linha = QHBoxLayout()
        self.filtro_input = QLineEdit()
        self.filtro_input.setPlaceholderText("Filtrar por nº do pedido (nome da pasta)")
        self.filtro_input.textChanged.connect(self._carregar_explorador)
        self.filtrar_btn = QPushButton("Filtrar")
        self.filtrar_btn.clicked.connect(self._carregar_explorador)
        filtro_linha.addWidget(self.filtro_input)
        filtro_linha.addWidget(self.filtrar_btn)
        layout.addLayout(filtro_linha)

        splitter = QSplitter()

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("Pastas (horizontal)"))
        self.pastas_list = QListWidget()
        self.pastas_list.setViewMode(QListWidget.IconMode)
        self.pastas_list.setFlow(QListWidget.LeftToRight)
        self.pastas_list.setWrapping(True)
        self.pastas_list.setResizeMode(QListWidget.Adjust)
        self.pastas_list.setIconSize(self._icone_padrao(self.style(), "SP_DirIcon").actualSize(self.pastas_list.iconSize()))
        self.pastas_list.currentItemChanged.connect(self._selecionar_pasta)
        left_layout.addWidget(self.pastas_list)

        left_layout.addWidget(QLabel("Arquivos da pasta"))
        self.arquivos_list = QListWidget()
        self.arquivos_list.currentItemChanged.connect(self._mostrar_imagem_unica)
        left_layout.addWidget(self.arquivos_list)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self.preview_label = QLabel("Selecione uma pasta para habilitar ações.")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        right_layout.addWidget(self.preview_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.hide()

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        right_layout.addWidget(self.scroll_area)

        self.acoes_layout = QHBoxLayout()
        self.abrir_tudo_btn = QPushButton("Abrir tudo")
        self.imprimir_btn = QPushButton("Imprimir")
        self.abrir_tudo_btn.clicked.connect(self._abrir_tudo)
        self.imprimir_btn.clicked.connect(self._imprimir_todos)
        self.abrir_tudo_btn.setEnabled(False)
        self.imprimir_btn.setEnabled(False)
        self.acoes_layout.addWidget(self.abrir_tudo_btn)
        self.acoes_layout.addWidget(self.imprimir_btn)
        self.acoes_layout.addStretch()
        right_layout.addLayout(self.acoes_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([480, 700])

        layout.addWidget(splitter)
        self.setLayout(layout)



    @staticmethod
    def _icone_padrao(style, nome_enum: str) -> QIcon:
        valor = None
        std = getattr(QStyle, "StandardPixmap", None)
        if std is not None:
            valor = getattr(std, nome_enum, None)
        if valor is None:
            valor = getattr(QStyle, nome_enum, None)
        if valor is None:
            return QIcon()
        return style.standardIcon(valor)

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
        self.pastas_list.clear()
        self.arquivos_list.clear()
        self.pasta_atual = None
        self.arquivos_da_pasta = []
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Selecione uma pasta para habilitar ações.")
        self.scroll_area.hide()
        self.abrir_tudo_btn.setEnabled(False)
        self.imprimir_btn.setEnabled(False)

        base = Path(BARCODES_DIR)
        if not base.exists():
            self.status_label.setText("Pasta de códigos não encontrada.")
            return

        filtro = self.filtro_input.text().strip().lower()
        pastas = sorted([p for p in base.iterdir() if p.is_dir()])
        if filtro:
            pastas = [p for p in pastas if filtro in p.name.lower()]

        if not pastas:
            self.status_label.setText("Nenhuma pasta encontrada para esse filtro.")
            return

        pasta_icon = self._icone_padrao(self.style(), "SP_DirIcon")
        total_arquivos = 0
        for pasta in pastas:
            qtd_png = len(list(pasta.glob("*.png")))
            total_arquivos += qtd_png
            item = QListWidgetItem(f"{pasta.name}\n({qtd_png})")
            item.setData(Qt.UserRole, str(pasta))
            item.setIcon(pasta_icon)
            self.pastas_list.addItem(item)

        self.status_label.setText(f"{len(pastas)} pasta(s) e {total_arquivos} arquivo(s) carregados.")
        self.pastas_list.setCurrentRow(0)

    def _selecionar_pasta(self, item_atual, _item_antigo):
        self.arquivos_list.clear()
        self.preview_label.setPixmap(QPixmap())
        self.preview_label.setText("Selecione um arquivo para pré-visualizar ou clique em 'Abrir tudo'.")
        self.scroll_area.hide()

        if not item_atual:
            self.pasta_atual = None
            self.arquivos_da_pasta = []
            self.abrir_tudo_btn.setEnabled(False)
            self.imprimir_btn.setEnabled(False)
            return

        self.pasta_atual = Path(item_atual.data(Qt.UserRole))
        self.arquivos_da_pasta = sorted(self.pasta_atual.glob("*.png"))

        file_icon = self._icone_padrao(self.style(), "SP_FileIcon")
        for arquivo in self.arquivos_da_pasta:
            item = QListWidgetItem(arquivo.name)
            item.setData(Qt.UserRole, str(arquivo))
            item.setIcon(file_icon)
            self.arquivos_list.addItem(item)

        possui_arquivos = len(self.arquivos_da_pasta) > 0
        self.abrir_tudo_btn.setEnabled(possui_arquivos)
        self.imprimir_btn.setEnabled(possui_arquivos)

        if possui_arquivos:
            self.arquivos_list.setCurrentRow(0)

    def _mostrar_imagem_unica(self, item_atual, _item_antigo):
        self.scroll_area.hide()
        self.preview_label.show()

        if not item_atual:
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Selecione um arquivo para pré-visualizar.")
            return

        pixmap = QPixmap(item_atual.data(Qt.UserRole))
        if pixmap.isNull():
            self.preview_label.setPixmap(QPixmap())
            self.preview_label.setText("Não foi possível carregar a imagem selecionada.")
            return

        self.preview_label.setPixmap(pixmap.scaled(620, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def _limpar_scroll_preview(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _abrir_tudo(self):
        if not self.arquivos_da_pasta:
            return

        self._limpar_scroll_preview()
        for arquivo in self.arquivos_da_pasta:
            titulo = QLabel(arquivo.name)
            titulo.setObjectName("subtitulo")
            self.scroll_layout.addWidget(titulo)

            img = QLabel()
            img.setAlignment(Qt.AlignCenter)
            pix = QPixmap(str(arquivo))
            if pix.isNull():
                img.setText(f"Falha ao carregar: {arquivo.name}")
            else:
                img.setPixmap(pix.scaled(620, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.scroll_layout.addWidget(img)

        self.preview_label.hide()
        self.scroll_area.show()

    @staticmethod
    def _calcular_area_impressao(printer: QPrinter, largura_px: int, altura_px: int) -> QRectF:
        pagina = printer.pageRect(QPrinter.DevicePixel)
        margem_x = pagina.width() * 0.08
        margem_y = pagina.height() * 0.08
        largura_max = pagina.width() - (margem_x * 2)
        altura_max = pagina.height() - (margem_y * 2)

        proporcao = largura_px / altura_px if altura_px else 1
        largura_destino = min(largura_max, pagina.width() * 0.84)
        altura_destino = largura_destino / proporcao if proporcao else altura_max

        if altura_destino > altura_max:
            altura_destino = altura_max
            largura_destino = altura_destino * proporcao

        x = pagina.x() + ((pagina.width() - largura_destino) / 2)
        y = pagina.y() + ((pagina.height() - altura_destino) / 2)
        return QRectF(x, y, largura_destino, altura_destino)

    def _imprimir_todos(self):
        if not self.arquivos_da_pasta:
            QMessageBox.warning(self, "Impressão", "Selecione uma pasta com etiquetas para imprimir.")
            return

        printer = QPrinter(QPrinter.HighResolution)
        printer.setFullPage(False)
        printer.setDocName(f"Etiquetas_{self.pasta_atual.name if self.pasta_atual else 'lote'}")

        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QPrintDialog.Accepted:
            return

        painter = QPainter()
        if not painter.begin(printer):
            QMessageBox.critical(self, "Impressão", "Não foi possível iniciar a impressão.")
            return

        try:
            for idx, arquivo in enumerate(self.arquivos_da_pasta):
                imagem = QPixmap(str(arquivo)).toImage()
                if imagem.isNull():
                    continue

                area_destino = self._calcular_area_impressao(printer, imagem.width(), imagem.height())
                painter.drawImage(area_destino, imagem)

                if idx < len(self.arquivos_da_pasta) - 1:
                    printer.newPage()
        finally:
            painter.end()

        QMessageBox.information(self, "Impressão", "Impressão em lote enviada com tamanho padronizado (1 etiqueta por página).")
