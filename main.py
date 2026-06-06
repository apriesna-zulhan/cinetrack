"""
CineTrack v2 — Katalog Film Desktop
Netflix-style UI · TMDb API · SQLite · PySide6

Cara menjalankan:
    pip install -r requirements.txt
    python main.py

Struktur folder:
    main.py               → Entry point
    config.py             → API key & konfigurasi
    api/
        tmdb_client.py    → TMDb REST API client
        workers.py        → QThread workers (fetch, image, search)
    database/
        db_manager.py     → SQLite CRUD lokal
    ui/
        theme.py          → Netflix dark theme + QSS
        main_window.py    → Jendela utama + sidebar + topbar
        pages/
            dashboard_page.py  → Statistik + chart
            movies_page.py     → Grid film + hero + detail
            favorites_page.py  → CRUD favorit
        components/
            movie_card.py      → Kartu film custom (QPainter)
            hero_banner.py     → Hero banner dengan backdrop
            image_cache.py     → Cache gambar di memori
            stat_card.py       → Kartu statistik
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

from ui.main_window import MainWindow


def main():
    # Aktifkan High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("CineTrack")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("CineTrack Dev")

    # Font default
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
