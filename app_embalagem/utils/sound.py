from PySide6.QtWidgets import QApplication


def beep_scan() -> None:
    app = QApplication.instance()
    if app:
        app.beep()
