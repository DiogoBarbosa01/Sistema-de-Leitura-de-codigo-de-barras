from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

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
        root = QVBoxLayout()

        titulo = QLabel("Painel de Produção")
        titulo.setObjectName("tituloDashboard")
        root.addWidget(titulo)

        detalhe = QLabel("Dados puxados do cadastro de caixas")
        detalhe.setObjectName("textoAux")
        root.addWidget(detalhe)

        cards_layout = QHBoxLayout()
        card_hoje, self.total_hoje_label = self._criar_card("Caixas cadastradas hoje")
        card_online, self.online_label = self._criar_card("Operadores online")
        cards_layout.addWidget(card_hoje)
        cards_layout.addWidget(card_online)
        root.addLayout(cards_layout)

        self.online_detalhe = QLabel("Online: -")
        self.online_detalhe.setObjectName("textoAux")
        root.addWidget(self.online_detalhe)

        topo_tabela = QHBoxLayout()
        subtitulo = QLabel("Últimos cadastros de caixa")
        subtitulo.setObjectName("subtitulo")

        atualizar_btn = QPushButton("Atualizar")
        atualizar_btn.clicked.connect(self._carregar)

        ultimo_dia_btn = QPushButton("Último dia")
        ultimo_dia_btn.clicked.connect(self._carregar_ultimo_dia)

        self.ultimo_dia_info = QLabel("Último dia: 0")
        self.ultimo_dia_info.setObjectName("textoAux")

        topo_tabela.addWidget(subtitulo)
        topo_tabela.addStretch()
        topo_tabela.addWidget(self.ultimo_dia_info)
        topo_tabela.addWidget(ultimo_dia_btn)
        topo_tabela.addWidget(atualizar_btn)

        self.mov_table = QTableWidget(0, 5)
        self.mov_table.setHorizontalHeaderLabels(["Código", "Nº Pedido", "Funcionário", "Status", "Criada em"])
        self.mov_table.verticalHeader().setVisible(False)
        self.mov_table.setAlternatingRowColors(True)

        root.addLayout(topo_tabela)
        root.addWidget(self.mov_table)
        self.setLayout(root)

    def _carregar_ultimo_dia(self):
        session = get_session()
        try:
            total = self.caixa_service.total_cadastradas_ultimo_dia(session)
            self.ultimo_dia_info.setText(f"Último dia: {total}")
        finally:
            session.close()

    def _carregar(self):
        session = get_session()
        try:
            total_hoje = self.caixa_service.total_cadastradas_hoje(session)
            online = self.caixa_service.operadores_online_por_cadastro(session, janela_minutos=15)

            self.total_hoje_label.setText(str(total_hoje))
            self.online_label.setText(str(len(online)))

            if online:
                self.online_detalhe.setText("Online: " + ", ".join([f"🟢 {nome}" for nome, _qtd in online]))
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
