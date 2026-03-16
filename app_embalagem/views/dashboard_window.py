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
from sqlalchemy import select

from app_embalagem.database.connection import get_session
from app_embalagem.models.funcionario import Funcionario
from app_embalagem.services.caixa_service import CaixaService
from app_embalagem.services.movimentacao_service import MovimentacaoService
from app_embalagem.utils.helpers import formatar_data_hora


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.caixa_service = CaixaService()
        self.mov_service = MovimentacaoService()
        self.setWindowTitle("Dashboard de Produção")
        self.resize(900, 560)
        self._montar_ui()
        self._carregar()

    def _criar_card(self, titulo: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setObjectName("card")
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

        cards_layout = QHBoxLayout()
        card_hoje, self.total_hoje_label = self._criar_card("Caixas embaladas hoje")
        card_pend, self.pendentes_label = self._criar_card("Caixas pendentes")
        card_prod, self.producao_label = self._criar_card("Funcionários produzindo")
        cards_layout.addWidget(card_hoje)
        cards_layout.addWidget(card_pend)
        cards_layout.addWidget(card_prod)
        root.addLayout(cards_layout)

        self.producao_detalhe = QLabel("Produção por funcionário: -")
        self.producao_detalhe.setObjectName("textoAux")
        root.addWidget(self.producao_detalhe)

        topo_tabela = QHBoxLayout()
        subtitulo = QLabel("Últimas movimentações")
        subtitulo.setObjectName("subtitulo")
        atualizar_btn = QPushButton("Atualizar")
        atualizar_btn.clicked.connect(self._carregar)
        topo_tabela.addWidget(subtitulo)
        topo_tabela.addStretch()
        topo_tabela.addWidget(atualizar_btn)

        self.mov_table = QTableWidget(0, 4)
        self.mov_table.setHorizontalHeaderLabels(["Caixa", "Funcionário", "Ação", "Data/Hora"])
        self.mov_table.verticalHeader().setVisible(False)
        self.mov_table.setAlternatingRowColors(True)

        root.addLayout(topo_tabela)
        root.addWidget(self.mov_table)

        self.setLayout(root)
        self.setStyleSheet(
            """
            QWidget { background-color: #121722; color: #e8eefc; font-size: 13px; }
            #tituloDashboard { font-size: 24px; font-weight: 700; color: #8cc8ff; margin-bottom: 6px; }
            #subtitulo { font-size: 16px; font-weight: 600; }
            #textoAux { color: #b8c2d9; margin: 4px 0 8px 0; }
            QFrame#card { background: #1b2333; border: 1px solid #33415f; border-radius: 12px; padding: 8px; }
            #cardTitulo { color: #98a4bf; font-size: 12px; }
            #cardValor { font-size: 28px; font-weight: 700; color: #f4f7ff; }
            QPushButton { background: #2d4f87; border: none; border-radius: 8px; padding: 8px 12px; }
            QPushButton:hover { background: #3d66ab; }
            QTableWidget { background-color: #0f1520; gridline-color: #2a354e; border: 1px solid #2a354e; }
            QHeaderView::section { background-color: #1d2738; padding: 6px; border: none; color: #dce6ff; }
            """
        )

    def _carregar(self):
        session = get_session()
        try:
            total_hoje = self.caixa_service.total_embaladas_hoje(session)
            pendentes = self.caixa_service.total_pendentes(session)
            producao = self.caixa_service.producao_por_funcionario(session)

            self.total_hoje_label.setText(str(total_hoje))
            self.pendentes_label.setText(str(pendentes))
            self.producao_label.setText(str(len(producao)))

            linhas_producao = []
            for funcionario_id, qtd in producao:
                funcionario = session.scalar(select(Funcionario).where(Funcionario.id == funcionario_id))
                nome = funcionario.nome if funcionario else f"ID {funcionario_id}"
                linhas_producao.append(f"{nome}: {qtd}")
            self.producao_detalhe.setText("Produção por funcionário: " + (", ".join(linhas_producao) if linhas_producao else "-"))

            ultimas = self.mov_service.ultimas(session)
            self.mov_table.setRowCount(len(ultimas))
            for i, mov in enumerate(ultimas):
                self.mov_table.setItem(i, 0, QTableWidgetItem(mov.caixa.codigo_caixa if mov.caixa else "-"))
                self.mov_table.setItem(i, 1, QTableWidgetItem(mov.funcionario.nome if mov.funcionario else "-"))
                self.mov_table.setItem(i, 2, QTableWidgetItem(mov.acao))
                self.mov_table.setItem(i, 3, QTableWidgetItem(formatar_data_hora(mov.data_hora)))

            self.mov_table.resizeColumnsToContents()
        finally:
            session.close()
