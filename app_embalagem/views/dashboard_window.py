from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app_embalagem.database.connection import get_session
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.utils.helpers import formatar_data_hora
from app_embalagem.utils.theme import APP_STYLESHEET


class DashboardWindow(QWidget):
    LIMITE_TABELA = 20

    def __init__(self):
        super().__init__()
        self.caixa_service = CaixaService()
        self.setWindowTitle("Dashboard de Produção")
        self.resize(980, 620)
        self._montar_ui()
        self.setStyleSheet(APP_STYLESHEET)
        self._carregar()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._carregar)
        self.timer.start(3000)

    def _criar_card(self, titulo: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("kpiCard")
        layout = QVBoxLayout(card)
        titulo_label = QLabel(titulo)
        titulo_label.setObjectName("cardTitulo")
        valor_label = QLabel("0")
        valor_label.setObjectName("cardValor")
        layout.addWidget(titulo_label)
        layout.addWidget(valor_label)
        return card, valor_label

    def _montar_ui(self):
        root = QHBoxLayout()

        centro = QVBoxLayout()

        titulo = QLabel("Painel de Produção")
        titulo.setObjectName("tituloDashboard")
        centro.addWidget(titulo)

        detalhe = QLabel("Dados puxados do cadastro de caixas")
        detalhe.setObjectName("textoAux")
        centro.addWidget(detalhe)

        cards_layout = QHBoxLayout()
        card_hoje, self.total_hoje_label = self._criar_card("Caixas cadastradas hoje")
        card_online, self.online_label = self._criar_card("Operadores online")
        cards_layout.addWidget(card_hoje)
        cards_layout.addWidget(card_online)
        centro.addLayout(cards_layout)

        self.online_detalhe = QLabel("Online: -")
        self.online_detalhe.setObjectName("textoAux")
        centro.addWidget(self.online_detalhe)

        topo_tabela = QHBoxLayout()
        subtitulo = QLabel("Últimos cadastros de caixa")
        subtitulo.setObjectName("subtitulo")

        self.ultimo_dia_info = QLabel("Último dia: 0")
        self.ultimo_dia_info.setObjectName("textoAux")

        topo_tabela.addWidget(subtitulo)
        topo_tabela.addStretch()
        topo_tabela.addWidget(self.ultimo_dia_info)

        self.mov_table = QTableWidget(0, 5)
        self.mov_table.setHorizontalHeaderLabels(["Código", "Nº Pedido", "Funcionário", "Status", "Criada em"])
        self.mov_table.verticalHeader().setVisible(False)
        self.mov_table.setAlternatingRowColors(True)

        centro.addLayout(topo_tabela)
        centro.addWidget(self.mov_table)

        profile = QFrame()
        profile.setObjectName("dashProfile")
        profile_layout = QVBoxLayout(profile)
        ptitle = QLabel("Perfil")
        ptitle.setObjectName("subtitulo")
        profile_layout.addWidget(ptitle)
        pcard = QFrame()
        pcard.setObjectName("kpiCard")
        pcard_layout = QVBoxLayout(pcard)
        pcard_layout.addWidget(QLabel("Supervisor"))
        pcard_layout.addWidget(QLabel("Operações"))
        profile_layout.addWidget(pcard)
        profile_layout.addWidget(QLabel("Notificações"))
        profile_layout.addWidget(QLabel("• Sincronização ativa"))
        profile_layout.addWidget(QLabel("• Dashboard atualizado"))
        profile_layout.addStretch()

        root.addLayout(centro, 8)
        root.addWidget(profile, 3)
        self.setLayout(root)
        self.setStyleSheet(APP_STYLESHEET + """
            QFrame#dashProfile { background:#ffffff; border-radius:18px; padding:8px; }
            QTableWidget { border-radius:14px; }
        """)

    def _carregar(self):
        session = get_session()
        try:
            total_hoje = self.caixa_service.total_cadastradas_hoje(session)
            total_ultimo_dia = self.caixa_service.total_cadastradas_ultimo_dia(session)
            online = self.caixa_service.operadores_online(session, janela_segundos=15)
            
            if not online:
                online = online or []

            self.total_hoje_label.setText(str(total_hoje))
            self.ultimo_dia_info.setText(f"Último dia: {total_ultimo_dia}")
            self.online_label.setText(str(len(online)))

            if online:
                self.online_detalhe.setText("Online: " + ", ".join([f"🟢 {u.nome}" for u in online]))
            else:
                self.online_detalhe.setText("Online: -")

            caixas = self.caixa_service.listar_recentes(session, limite=self.LIMITE_TABELA)
            self.mov_table.setRowCount(len(caixas))
            for i, caixa in enumerate(caixas):
                self.mov_table.setItem(i, 0, QTableWidgetItem(caixa.codigo_caixa))
                self.mov_table.setItem(i, 1, QTableWidgetItem(caixa.arte))
                self.mov_table.setItem(i, 2, QTableWidgetItem(caixa.nome_funcionario))
                self.mov_table.setItem(i, 3, QTableWidgetItem(caixa.status))
                self.mov_table.setItem(i, 4, QTableWidgetItem(formatar_data_hora(caixa.data_criacao)))

            self.mov_table.resizeColumnsToContents()
        finally:
            session.close()
