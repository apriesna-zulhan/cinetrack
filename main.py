import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from ui.main_window import MainWindow
from ui.theme import load_qss


def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("CineTrack")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("CineTrack Dev")

    app.setFont(QFont("Segoe UI", 10))

    qss = load_qss()
    if qss:
        app.setStyleSheet(qss)

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
