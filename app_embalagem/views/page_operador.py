from calendar import monthrange
from datetime import date, datetime

from PySide6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QFont
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QGraphicsTextItem

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
        brand = QLabel("Embalagem")
        brand.setObjectName("opBrand")
        side_layout.addWidget(brand)

        self.menu = QListWidget()
        for item in [
            "Buscar Caixa",
            "Dashboard",
            "Cadastro de Caixa",
            "Código de Barras",
            "Receita de Metros",
            "Receita de Caixas",
            "Sair",
        ]:
            QListWidgetItem(item, self.menu)
        self.menu.setCurrentRow(1)
        self.menu.itemClicked.connect(self._acao_menu)
        side_layout.addWidget(self.menu)

        center = QVBoxLayout()
        header = QHBoxLayout()
        titulo = QLabel("Dashboard do Operador")
        titulo.setObjectName("tituloDashboard")
        header.addWidget(titulo)
        header.addStretch()
        center.addLayout(header)

        subtitulo = QLabel("Acompanhamento mensal de redução de metros e total de caixas cadastradas.")
        subtitulo.setObjectName("subtitulo")
        center.addWidget(subtitulo)

        graficos = QHBoxLayout()
        graficos.setAlignment(Qt.AlignTop)
        self.chart_metros_view = QChartView()
        self.chart_caixas_view = QChartView()
        self.chart_metros_view.setRenderHint(QPainter.Antialiasing)
        self.chart_caixas_view.setRenderHint(QPainter.Antialiasing)
        self.chart_metros_view.setMinimumHeight(280)
        self.chart_metros_view.setMaximumHeight(320)
        self.chart_caixas_view.setMinimumHeight(280)
        self.chart_caixas_view.setMaximumHeight(320)
        graficos.addWidget(self.chart_metros_view, 2)
        graficos.addWidget(self.chart_caixas_view, 1)
        center.addLayout(graficos)
        center.addStretch()

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
            QWidget { background: #F5F7FB; }
            QFrame#opSidebar { background:#ffffff; border-radius:18px; color:#111827; border:none; outline:none; }
            QLabel#opBrand { color:#111827; font-size:24px; font-weight:700; padding:10px; }
            QListWidget { background:transparent; border:none; color:#111827; outline:none; }
            QFrame#opSidebar:focus, QListWidget:focus { border:none; outline:none; }
            QListWidget::item { padding:10px; border-radius:10px; margin:2px 0; border:none; }
            QListWidget::item:hover { background:#f3f4f6; border:none; }
            QListWidget::item:selected { background:#ede9fe; color:#7c3aed; border:none; }
            QFrame#opProfile { background:#ffffff; border-radius:18px; padding:10px; border:1px solid #ececf1; }
            QFrame#opProfileCard { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #C4B5FD, stop:1 #8B5CF6); color:#ffffff; border-radius:14px; min-height:120px; }
            QChartView { background:#ffffff; border-radius:16px; border:1px solid #ececf1; min-height:280px; max-height:320px; }
        """
        )

        self._atualizar_graficos()

    def _acao_menu(self, item):
        opcoes = {
            "Buscar Caixa": self.abrir_scanner,
            "Dashboard": self.abrir_dashboard,
            "Cadastro de Caixa": self.abrir_cadastro_caixa,
            "Código de Barras": self.abrir_codigos,
            "Sair": self.close,
        }
        acao = opcoes.get(item.text())
        if acao:
            acao()

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
            total_metros = sum(por_dia_metros.values())

            stmt_caixas = (
                select(func.date(Caixa.data_criacao), func.count(Caixa.id))
                .where(Caixa.data_criacao.between(inicio_mes, fim_mes))
                .group_by(func.date(Caixa.data_criacao))
                .order_by(func.date(Caixa.data_criacao))
            )
            resultados_caixas = session.execute(stmt_caixas).all()
            por_dia_caixas = {int(str(dia).split("-")[-1]): int(total or 0) for dia, total in resultados_caixas}
            total_caixas = sum(por_dia_caixas.values())

            online = session.execute(
                select(func.count(func.distinct(Caixa.nome_funcionario))).where(Caixa.data_criacao >= datetime.now().replace(minute=0, second=0, microsecond=0))
            ).scalar() or 0
            self.online_stats_label.setText(f"👥 Online: {online}")
        finally:
            session.close()

            chart_metros = QChart()
            chart_metros.setTitle(f" TOTAL DE METROS NO MÊS")
            chart_metros.legend().hide()

            donut_metros = QPieSeries()
            donut_metros.setHoleSize(0.65)
            dias_com_metros = len([v for v in por_dia_metros.values() if v > 0])
            dias_sem_metros = max(ultimo_dia - dias_com_metros, 0)

            fatia_metros = QPieSlice("Com metros", float(total_metros if total_metros > 0 else 1))
            fatia_sem_metros = QPieSlice("Sem metros", float(dias_sem_metros if dias_sem_metros > 0 else 1))
            fatia_metros.setColor(QColor("#8B5CF6"))
            fatia_sem_metros.setColor(QColor("#FDBA74"))

            donut_metros.append(fatia_metros)
            donut_metros.append(fatia_sem_metros)
            chart_metros.addSeries(donut_metros)
            chart_metros.setBackgroundVisible(False)
            self.chart_metros_view.setChart(chart_metros)
            self.chart_metros_view.setRenderHint(QPainter.Antialiasing)
        
            texto_centro = QGraphicsTextItem (f"{total_metros:.1f}m")
            texto_centro.setDefaultTextColor(QColor("#0552F7"))
            font =QFont("Arial", 14)
            font.setBold(True)
            texto_centro.setFont(font)
            self.chart_metros_view.scene().addItem(texto_centro)
        
            QTimer.singleShot(0, lambda: texto_centro.setPos(
            chart_metros.plotArea().center().x() - texto_centro.boundingRect().width() / 2,
            chart_metros.plotArea().center().y() - texto_centro.boundingRect().height() / 2
        ))
         
        chart_caixas = QChart()
        chart_caixas.setTitle("Device • Receita de Caixas")
        chart_caixas.legend().hide()
   
    
        donut = QPieSeries()
        donut.setHoleSize(0.65)
        com_caixa = QPieSlice("Com cadastro", float(total_caixas))
        sem_caixa = QPieSlice("Sem cadastro", float(max(ultimo_dia - len([x for x in por_dia_caixas.values() if x > 0]), 0)))
        com_caixa.setColor(QColor("#8B5CF6"))
        sem_caixa.setColor(QColor("#FDBA74"))
        donut.append(com_caixa)
        donut.append(sem_caixa)
        chart_caixas.addSeries(donut)

        centro = chart_caixas.title()
        chart_caixas.setTitle(f"Caixas Embaladas no mês • Total: {total_caixas}")
        chart_caixas.setBackgroundVisible(False)
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
