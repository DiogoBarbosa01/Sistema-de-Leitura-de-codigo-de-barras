APP_STYLESHEET = """
QWidget {
    background-color: #0b1020;
    color: #eef4ff;
    font-size: 13px;
    font-family: 'Segoe UI', 'Inter', Arial;
}

QLabel#tituloPagina {
    font-size: 24px;
    font-weight: 800;
    color: #7dd3fc;
    margin-bottom: 10px;
}

QLabel#subtitulo {
    font-size: 15px;
    font-weight: 600;
    color: #c8d8ff;
}

QLineEdit,
QComboBox,
QTableWidget,
QListWidget {
    background-color: #111a30;
    border: 1px solid #2b3a64;
    border-radius: 10px;
    padding: 8px;
    color: #f7fbff;
    selection-background-color: #2563eb;
}

QLineEdit:focus,
QComboBox:focus,
QTableWidget:focus,
QListWidget:focus {
    border: 1px solid #60a5fa;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2563eb, stop:1 #1d4ed8);
    border: none;
    border-radius: 10px;
    padding: 9px 14px;
    color: #f8fbff;
    font-weight: 600;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3b82f6, stop:1 #2563eb);
}

QPushButton:disabled {
    background: #334155;
    color: #94a3b8;
}

QTableWidget {
    gridline-color: #24304f;
    alternate-background-color: #0f172a;
}

QHeaderView::section {
    background-color: #18223d;
    padding: 7px;
    border: none;
    color: #dbeafe;
    font-weight: 600;
}

QFrame#card {
    background: #131d34;
    border: 1px solid #33466f;
    border-radius: 14px;
    padding: 10px;
}

QMessageBox {
    background-color: #0f172a;
}
"""
