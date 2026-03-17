APP_STYLESHEET = """
QWidget {
    background-color: #f5f7fb;
    color: #1f2937;
    font-size: 13px;
    font-family: 'Segoe UI', 'Inter', Arial;
}

QLabel#tituloPagina,
QLabel#tituloDashboard,
QLabel#tituloLogin {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
}

QLabel#subtitulo,
QLabel#textoAux,
QLabel#loginHint,
QLabel#tableHint {
    font-size: 13px;
    color: #6b7280;
}

QFrame#card {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px;
}

QFrame#kpiCard {
    background-color: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 10px;
}

QLabel#cardTitulo {
    color: #6b7280;
    font-size: 12px;
}

QLabel#cardValor {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

QLineEdit,
QComboBox,
QTableWidget,
QListWidget {
    background-color: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    padding: 8px;
    color: #111827;
    selection-background-color: #2563eb;
    selection-color: #ffffff;
}

QLineEdit:focus,
QComboBox:focus,
QTableWidget:focus,
QListWidget:focus {
    border: 1px solid #2563eb;
}

QPushButton {
    background-color: #2563eb;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    color: #ffffff;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #9ca3af;
    color: #f9fafb;
}

QPushButton#secondaryButton {
    background-color: #e5e7eb;
    color: #1f2937;
}

QPushButton#secondaryButton:hover {
    background-color: #d1d5db;
}

QTableWidget {
    gridline-color: #e5e7eb;
    alternate-background-color: #f9fafb;
}

QHeaderView::section {
    background-color: #f3f4f6;
    padding: 7px;
    border: none;
    color: #374151;
    font-weight: 600;
}

QMessageBox {
    background-color: #ffffff;
}
"""
