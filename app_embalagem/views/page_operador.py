from calendar import monthrange
from datetime import date, datetime

from PySide6.QtCharts import QBarCategoryAxis, QBarSeries, QBarSet, QChart, QChartView, QLineSeries, QValueAxis
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import func, select

from app_embalagem.database.connection import get_session
from app_embalagem.models.caixa import Caixa
from app_embalagem.services.mobile_request_service import MobileRequestService
from app_embalagem.services.mobile_usb_service import MobileUsbService
from app_embalagem.services.scan_service import ScanService
from app_embalagem.utils.sound import beep_scan
from app_embalagem.utils.theme import APP_STYLESHEET
from app_embalagem.views.caixa_detalhes_dialog import CaixaDetalhesDialog
from app_embalagem.views.cadastro_caixa_window import CadastroCaixaWindow
from app_embalagem.views.codigos_barras_window import CodigosBarrasWindow
from app_embalagem.views.dashboard_window import DashboardWindow
from app_embalagem.views.scanner_window import ScannerWindow


class PageOperador(QWidget):
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.scan_service = ScanService()
        self.mobile_usb_service = MobileUsbService()
        self.mobile_request_service = MobileRequestService()
        self.setWindowTitle(f"Página Operador - {usuario.nome}")
        self.resize(1380, 780)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)

        try:
            self.mobile_request_service.iniciar()
        except Exception:
            pass

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._monitorar)
        self.timer.start(1800)

    def _montar_ui(self):
        layout = QHBoxLayout()

        sidebar = QFrame()
        sidebar.setObjectName("opSidebar")
        side_layout = QVBoxLayout(sidebar)
        brand = QLabel("AnicornApp")
        brand.setObjectName("opBrand")
        side_layout.addWidget(brand)
        menu = QListWidget()
        for item in [
            "Buscar Caixa",
            "Dashboard",
            "Cadastro de Caixa",
            "Código de Barras",
            "Receita de Metros",
            "Receita de Caixas",
            "Sair",
        ]:
            QListWidgetItem(item, menu)
        menu.setCurrentRow(1)
        side_layout.addWidget(menu)

        center = QVBoxLayout()
        header = QHBoxLayout()
        titulo = QLabel("Dashboard do Operador")
        titulo.setObjectName("tituloDashboard")
        header.addWidget(titulo)
        header.addStretch()
        center.addLayout(header)

        subtitulo = QLabel(
            "Acompanhamento mensal de redução de metros e total de caixas cadastradas."
        )
        subtitulo.setObjectName("subtitulo")
        center.addWidget(subtitulo)

        botoes = QGridLayout()
        self.scanner_btn = QPushButton("Buscar Caixa")
        self.cadastro_caixa_btn = QPushButton("Cadastro de Caixa")
        self.dash_btn = QPushButton("Dashboard")
        self.codigos_btn = QPushButton("Código de Barras")

        self.scanner_btn.clicked.connect(self.abrir_scanner)
        self.cadastro_caixa_btn.clicked.connect(self.abrir_cadastro_caixa)
        self.dash_btn.clicked.connect(self.abrir_dashboard)
        self.codigos_btn.clicked.connect(self.abrir_codigos)

        botoes.addWidget(self.scanner_btn, 0, 0)
        botoes.addWidget(self.dash_btn, 0, 1)
        botoes.addWidget(self.cadastro_caixa_btn, 1, 0)
        botoes.addWidget(self.codigos_btn, 1, 1)
        center.addLayout(botoes)

        graficos = QHBoxLayout()
        self.chart_metros_view = QChartView()
        self.chart_caixas_view = QChartView()
        self.chart_metros_view.setRenderHint(QPainter.Antialiasing)
        self.chart_caixas_view.setRenderHint(QPainter.Antialiasing)
        graficos.addWidget(self.chart_metros_view, 1)
        graficos.addWidget(self.chart_caixas_view, 1)
        center.addLayout(graficos, 1)

        profile = QFrame()
        profile.setObjectName("opProfile")
        profile_layout = QVBoxLayout(profile)
        profile_layout.addWidget(QLabel("Profile"))
        card = QFrame()
        card.setObjectName("opProfileCard")
        card_layout = QVBoxLayout(card)
        name = QLabel(self.usuario.nome)
        name.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(name)
        card_layout.addWidget(QLabel("Operador"), alignment=Qt.AlignCenter)
        profile_layout.addWidget(card)

        self.online_stats_label = QLabel("👥 Online: --")
        self.host_status_label = QLabel("🖥 Host: inválido")
        self.mobile_status_label = QLabel("📱 Celular: inválido")
        self.scanner_status_label = QLabel("📷 Scanner: pronto")
        profile_layout.addWidget(self.online_stats_label)
        profile_layout.addWidget(self.host_status_label)
        profile_layout.addWidget(self.mobile_status_label)
        profile_layout.addWidget(self.scanner_status_label)
        profile_layout.addWidget(QLabel("🔎 Search"))
        profile_layout.addWidget(QLabel("🔔 Notification"))
        profile_layout.addStretch()

        layout.addWidget(sidebar, 2)
        layout.addLayout(center, 8)
        layout.addWidget(profile, 3)
        self.setLayout(layout)
        self.setStyleSheet(
            APP_STYLESHEET
            + """
            QFrame#opSidebar { background:#6D28D9; border-radius:18px; color:white; }
            QLabel#opBrand { color:white; font-size:24px; font-weight:700; padding:10px; }
            QListWidget { background:transparent; border:none; color:white; }
            QListWidget::item { padding:10px; border-radius:10px; margin:2px 0; }
            QListWidget::item:selected { background:#fb7185; color:white; }
            QFrame#opProfile { background:#ffffff; border-radius:18px; padding:10px; }
            QFrame#opProfileCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #FDBA74, stop:1 #FB7185); border-radius:14px; min-height:120px; }
            QChartView { background:#ffffff; border-radius:14px; border:1px solid #ececf1; min-height:290px; }
        """
        )

        self._atualizar_graficos()

    def _atualizar_graficos(self):
        hoje = date.today()
        ano, mes = hoje.year, hoje.month
        ultimo_dia = monthrange(ano, mes)[1]

        session = get_session()
        try:
            inicio_mes = datetime(ano, mes, 1)
            fim_mes = datetime(ano, mes, ultimo_dia, 23, 59, 59)

            stmt_metros = (
                select(func.date(Caixa.data_criacao), func.sum(Caixa.metros))
                .where(Caixa.data_criacao.between(inicio_mes, fim_mes))
                .group_by(func.date(Caixa.data_criacao))
                .order_by(func.date(Caixa.data_criacao))
            )
            resultados_metros = session.execute(stmt_metros).all()
            por_dia_metros = {int(str(dia).split("-")[-1]): float(total or 0) for dia, total in resultados_metros}

            stmt_caixas = (
                select(func.date(Caixa.data_criacao), func.count(Caixa.id))
                .where(Caixa.data_criacao.between(inicio_mes, fim_mes))
                .group_by(func.date(Caixa.data_criacao))
                .order_by(func.date(Caixa.data_criacao))
            )
            resultados_caixas = session.execute(stmt_caixas).all()
            por_dia_caixas = {int(str(dia).split("-")[-1]): int(total or 0) for dia, total in resultados_caixas}

            online = session.execute(
                select(func.count(func.distinct(Caixa.nome_funcionario))).where(Caixa.data_criacao >= datetime.now().replace(minute=0, second=0, microsecond=0))
            ).scalar() or 0
            self.online_stats_label.setText(f"👥 Online: {online}")
        finally:
            session.close()

        linha = QLineSeries()
        acumulado = 0.0
        for dia in range(1, ultimo_dia + 1):
            acumulado += por_dia_metros.get(dia, 0.0)
            linha.append(dia, acumulado)

        chart_metros = QChart()
        chart_metros.addSeries(linha)
        chart_metros.setTitle("Redução de metros no mês (acumulado diário)")
        axis_x = QValueAxis()
        axis_x.setTitleText("Dia do mês")
        axis_x.setRange(1, ultimo_dia)
        axis_x.setLabelFormat("%d")
        axis_y = QValueAxis()
        axis_y.setTitleText("Metros")
        chart_metros.addAxis(axis_x, Qt.AlignBottom)
        chart_metros.addAxis(axis_y, Qt.AlignLeft)
        linha.attachAxis(axis_x)
        linha.attachAxis(axis_y)
        self.chart_metros_view.setChart(chart_metros)

        bar_set = QBarSet("Caixas cadastradas")
        categorias = [str(d) for d in range(1, ultimo_dia + 1)]
        for dia in range(1, ultimo_dia + 1):
            bar_set.append(por_dia_caixas.get(dia, 0))
        bar_series = QBarSeries()
        bar_series.append(bar_set)

        chart_caixas = QChart()
        chart_caixas.addSeries(bar_series)
        chart_caixas.setTitle("Total de caixas cadastradas no mês")
        axis_cat = QBarCategoryAxis()
        axis_cat.append(categorias)
        axis_cat.setTitleText("Dia do mês")
        axis_bar_y = QValueAxis()
        axis_bar_y.setTitleText("Quantidade")
        chart_caixas.addAxis(axis_cat, Qt.AlignBottom)
        chart_caixas.addAxis(axis_bar_y, Qt.AlignLeft)
        bar_series.attachAxis(axis_cat)
        bar_series.attachAxis(axis_bar_y)
        self.chart_caixas_view.setChart(chart_caixas)

    def closeEvent(self, event):
        self.mobile_request_service.parar()
        super().closeEvent(event)

    def _processar_codigo(self, codigo: str):
        session = get_session()
        try:
            resultado = self.scan_service.buscar_caixa_por_codigo(session, codigo)
            if not resultado["ok"]:
                return
            beep_scan()
            CaixaDetalhesDialog(resultado["caixa"], self).exec()
        finally:
            session.close()

    def _monitorar(self):
        status_mobile = self.mobile_usb_service.status_conexao().conectado
        self.mobile_status_label.setText(f"📱 Celular: {'🟢 conectado' if status_mobile else '🔴 inválido'}")

        status_host = self.mobile_request_service.status().ativo
        self.host_status_label.setText(f"🖥 Host: {'🟢 conectado' if status_host else '🔴 inválido'}")

        codigo_request = self.mobile_request_service.ler_codigo()
        if codigo_request:
            self._processar_codigo(codigo_request)
            return

        codigo_usb = self.mobile_usb_service.ler_codigo_usb()
        if codigo_usb:
            self._processar_codigo(codigo_usb)

    def abrir_scanner(self):
        self.w_scanner = ScannerWindow()
        self.w_scanner.show()

    def abrir_cadastro_caixa(self):
        self.w_cadastro_caixa = CadastroCaixaWindow()
        self.w_cadastro_caixa.show()

    def abrir_dashboard(self):
        self.w_dash = DashboardWindow()
        self.w_dash.show()

    def abrir_codigos(self):
        self.w_codigos = CodigosBarrasWindow()
        self.w_codigos.show()
