import sys

from PySide6.QtWidgets import QApplication

from app_embalagem.config import APP_TITLE
from app_embalagem.database.init_db import init_db
from app_embalagem.views.login_window import LoginWindow


def main():
    init_db()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    window = LoginWindow()
    window.resize(420, 220)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
