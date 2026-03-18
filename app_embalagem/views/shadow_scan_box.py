from PySide6.QtCore import QEvent, QObject, QTimer, Qt, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget

from app_embalagem.services.scan_service import ScanService


class ShadowScanBox(QWidget):
    codigo_detectado = Signal(str)

    def __init__(self, parent=None, tamanho_minimo_codigo: int = 20):
        super().__init__(parent)
        self.tamanho_minimo_codigo = tamanho_minimo_codigo
        self.scan_service = ScanService()
        self._buffer = ""
        self._instalada = False
        self._montar_ui()
        self._configurar_timer()
        self._configurar_janela()

    def _montar_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scan_input = QLineEdit()
        self.scan_input.setObjectName("shadowScanInput")
        self.scan_input.setReadOnly(True)
        self.scan_input.setMaxLength(self.tamanho_minimo_codigo + 8)
        self.scan_input.setFixedSize(1, 1)
        layout.addWidget(self.scan_input)

    def _configurar_timer(self):
        self.reset_timer = QTimer(self)
        self.reset_timer.setSingleShot(True)
        self.reset_timer.setInterval(250)
        self.reset_timer.timeout.connect(self.limpar)

    def _configurar_janela(self):
        self.setWindowTitle("Shadow Scan Box")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowOpacity(0.01)
        self.setFixedSize(1, 1)
        tela = QGuiApplication.primaryScreen()
        if tela:
            area = tela.availableGeometry()
            self.move(area.right() - 2, area.bottom() - 2)

    def iniciar(self):
        self.show()
        app = QGuiApplication.instance()
        if app and not self._instalada:
            app.installEventFilter(self)
            self._instalada = True

    def parar(self):
        app = QGuiApplication.instance()
        if app and self._instalada:
            app.removeEventFilter(self)
            self._instalada = False
        self.limpar()

    def limpar(self):
        self._buffer = ""
        self.scan_input.clear()
        self.reset_timer.stop()

    def _adicionar_caractere(self, texto: str):
        self._buffer = f"{self._buffer}{texto}"[-(self.tamanho_minimo_codigo + 8) :]
        self.scan_input.setText(self._buffer)
        self.reset_timer.start()
        self._tentar_emitir_codigo()

    def _tentar_emitir_codigo(self):
        if len(self._buffer) < self.tamanho_minimo_codigo:
            return

        if "CX-" not in self._buffer.upper():
            return

        codigo = self.scan_service._extrair_codigo_caixa(self._buffer)
        if len(codigo) < self.tamanho_minimo_codigo:
            return

        self.codigo_detectado.emit(codigo)
        self.limpar()

    def eventFilter(self, _obj: QObject, event: QEvent):
        if event.type() != QEvent.KeyPress:
            return False

        if event.modifiers() & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier):
            return False

        tecla = event.key()
        if tecla in (Qt.Key_Return, Qt.Key_Enter):
            self._tentar_emitir_codigo()
            return False

        texto = (event.text() or "").strip()
        if not texto:
            return False

        if texto.isprintable():
            self._adicionar_caractere(texto.upper())
        return False
