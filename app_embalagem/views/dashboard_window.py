from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app_embalagem.database.connection import get_session
from app_embalagem.services.movimentacao_service import MovimentacaoService
from app_embalagem.utils.helpers import formatar_data_hora
from app_embalagem.utils.theme import APP_STYLESHEET


class DashboardWindow(QWidget):
    LIMITE_TABELA = 20

    def __init__(self):
        super().__init__()
        self.mov_service = MovimentacaoService()
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

        detalhe = QLabel("Visão geral de produtividade e movimentações recentes")
        detalhe.setObjectName("textoAux")
        root.addWidget(detalhe)

        cards_layout = QHBoxLayout()
        card_hoje, self.total_hoje_label = self._criar_card("Caixas embaladas hoje")
        card_ultimo_dia, self.ultimo_dia_card_label = self._criar_card("Caixas fechadas no último dia")
        card_online, self.online_label = self._criar_card("Funcionários produzindo (online)")
        cards_layout.addWidget(card_hoje)
        cards_layout.addWidget(card_ultimo_dia)
        cards_layout.addWidget(card_online)
        root.addLayout(cards_layout)

        self.online_detalhe = QLabel("Online: -")
        self.online_detalhe.setObjectName("textoAux")
        root.addWidget(self.online_detalhe)

        topo_tabela = QHBoxLayout()
        subtitulo = QLabel("Últimas movimentações")
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

        self.mov_table = QTableWidget(0, 4)
        self.mov_table.setHorizontalHeaderLabels(["Caixa", "Funcionário", "Ação", "Data/Hora"])
        self.mov_table.verticalHeader().setVisible(False)
        self.mov_table.setAlternatingRowColors(True)

        root.addLayout(topo_tabela)
        root.addWidget(self.mov_table)

        self.setLayout(root)

    def _carregar_ultimo_dia(self):
        session = get_session()
        try:
            total = self.mov_service.total_finalizadas_ultimo_dia(session)
            self.ultimo_dia_card_label.setText(str(total))
            self.ultimo_dia_info.setText(f"Último dia: {total}")
        finally:
            session.close()

    def _carregar(self):
        session = get_session()
        try:
            total_hoje = self.mov_service.total_finalizadas_hoje(session)
            total_ultimo_dia = self.mov_service.total_finalizadas_ultimo_dia(session)
            online = self.mov_service.operadores_online(session, janela_minutos=10)

            self.total_hoje_label.setText(str(total_hoje))
            self.ultimo_dia_card_label.setText(str(total_ultimo_dia))
            self.ultimo_dia_info.setText(f"Último dia: {total_ultimo_dia}")
            self.online_label.setText(str(len(online)))

            if online:
                descricoes = [f"🟢 {nome}" for _id, nome, _qtd, _ultima in online]
                self.online_detalhe.setText("Online: " + ", ".join(descricoes))
            else:
                self.online_detalhe.setText("Online: -")

            # mantém tabela rolante com tamanho fixo: novos entram no topo e os mais antigos saem no fim
            ultimas = self.mov_service.ultimas(session, limite=self.LIMITE_TABELA)
            self.mov_table.setRowCount(len(ultimas))
            for i, mov in enumerate(ultimas):
                self.mov_table.setItem(i, 0, QTableWidgetItem(mov.caixa.codigo_caixa if mov.caixa else "-"))
                self.mov_table.setItem(i, 1, QTableWidgetItem(mov.funcionario.nome if mov.funcionario else "-"))
                self.mov_table.setItem(i, 2, QTableWidgetItem(mov.acao))
                self.mov_table.setItem(i, 3, QTableWidgetItem(formatar_data_hora(mov.data_hora)))

            self.mov_table.resizeColumnsToContents()
        finally:
            session.close()
