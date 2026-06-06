"""
ui/main_window.py — MainWindow dengan cleanup thread yang benar.
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QStatusBar
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QPen

from config import APP_NAME, APP_VERSION, WINDOW_W, WINDOW_H, TMDB_API_KEY
from api.tmdb_client import TMDbClient
from ui.pages.dashboard_page import DashboardPage
from ui.pages.movies_page import MoviesPage
from ui.pages.favorites_page import FavoritesPage
from ui.theme import (QSS, BG_BASE, BG_SURFACE, WHITE, GRAY_200,
                       GRAY_300, GRAY_400, RED, GOLD, GREEN_ACT, BORDER)


class NavButton(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self._icon  = icon
        self._label = label
        self.setObjectName("nav_btn")
        self.setFixedHeight(46)
        self.setCursor(Qt.PointingHandCursor)
        self.set_active(False)

    def set_active(self, v: bool):
        self.setProperty("active", v)
        self.style().unpolish(self)
        self.style().polish(self)
        self.setText(f"   {self._icon}   {self._label}")


class Sidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(250)
        self._build()

    def _build(self):
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Logo
        logo_f = QFrame()
        logo_f.setFixedHeight(72)
        logo_f.setStyleSheet(
            f"background: #0D0D0D; border-bottom: 1px solid {BORDER};"
        )
        ll = QHBoxLayout(logo_f)
        ll.setContentsMargins(20, 0, 20, 0)

        icon_box = QFrame()
        icon_box.setFixedSize(32, 32)
        icon_box.setStyleSheet(f"background: {RED}; border-radius: 6px;")
        ib_lay = QHBoxLayout(icon_box)
        ib_lay.setContentsMargins(0, 0, 0, 0)
        ib = QLabel("▶")
        ib.setAlignment(Qt.AlignCenter)
        ib.setStyleSheet("color: white; font-size: 12px; background: transparent;")
        ib_lay.addWidget(ib)

        lbl_logo = QLabel(APP_NAME.upper())
        lbl_logo.setObjectName("logo_text")
        lbl_logo.setFont(QFont("Segoe UI", 14, QFont.Black))

        ll.addWidget(icon_box)
        ll.addSpacing(10)
        ll.addWidget(lbl_logo)
        ll.addStretch()
        lay.addWidget(logo_f)
        lay.addSpacing(16)

        def section(t):
            l = QLabel(t)
            l.setObjectName("nav_section")
            l.setFixedHeight(28)
            l.setFont(QFont("Segoe UI", 8, QFont.Bold))
            lay.addWidget(l)

        section("MENU UTAMA")
        self.btn_dashboard = NavButton("⊞", "Dashboard")
        self.btn_movies    = NavButton("🎬", "Film Populer")
        lay.addWidget(self.btn_dashboard)
        lay.addWidget(self.btn_movies)

        lay.addSpacing(8)
        section("KOLEKSI")
        self.btn_favorites = NavButton("❤️", "Favorit Saya")
        lay.addWidget(self.btn_favorites)
        lay.addStretch()

        # Info bawah
        info = QFrame()
        info.setStyleSheet(
            f"background: #0D0D0D; border-top: 1px solid {BORDER};"
        )
        il = QVBoxLayout(info)
        il.setContentsMargins(20, 12, 20, 16)
        il.setSpacing(6)

        self.lbl_api = QLabel("● TMDb API · Menghubungkan...")
        self.lbl_api.setStyleSheet(f"color: {GOLD}; font-size: 10px;")
        self.lbl_db  = QLabel("● SQLite · cinetrack.db")
        self.lbl_db.setStyleSheet(f"color: #4DA3FF; font-size: 10px;")
        lbl_ver = QLabel(f"{APP_NAME} v{APP_VERSION}  ·  PySide6")
        lbl_ver.setStyleSheet(f"color: {GRAY_400}; font-size: 9px;")

        il.addWidget(self.lbl_api)
        il.addWidget(self.lbl_db)
        il.addWidget(lbl_ver)
        lay.addWidget(info)

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#0D0D0D"))
        p.setPen(QPen(QColor(BORDER), 1))
        p.drawLine(self.width() - 1, 0, self.width() - 1, self.height())


class Topbar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topbar")
        self.setFixedHeight(56)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(32, 0, 32, 0)

        self.lbl_page = QLabel("Film Populer")
        self.lbl_page.setFont(QFont("Segoe UI", 15, QFont.Bold))
        self.lbl_page.setStyleSheet(f"color: {WHITE};")

        self.lbl_date = QLabel()
        self.lbl_date.setStyleSheet(f"color: {GRAY_400}; font-size: 11px;")

        lay.addWidget(self.lbl_page)
        lay.addStretch()
        lay.addWidget(self.lbl_date)

        self._update_date()
        t = QTimer(self)
        t.timeout.connect(self._update_date)
        t.start(60_000)

    def _update_date(self):
        self.lbl_date.setText(
            QDateTime.currentDateTime().toString("dddd, d MMMM yyyy  ·  HH:mm")
        )

    def set_page(self, name: str):
        self.lbl_page.setText(name)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Katalog Film Desktop")
        self.setMinimumSize(WINDOW_W, WINDOW_H)
        self.setStyleSheet(QSS)
        self._client  = TMDbClient(TMDB_API_KEY)
        self._api_req = 0
        self._build()
        self._navigate(0)   

    def _build(self):
        central = QWidget()
        central.setObjectName("root_widget")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._sidebar = Sidebar()
        self._sidebar.btn_dashboard.clicked.connect(lambda: self._navigate(0))
        self._sidebar.btn_movies.clicked.connect(lambda: self._navigate(1))
        self._sidebar.btn_favorites.clicked.connect(lambda: self._navigate(2))
        root.addWidget(self._sidebar)

        right = QWidget()
        right.setStyleSheet(f"background: {BG_BASE};")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)

        self._topbar = Topbar()
        rl.addWidget(self._topbar)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background: {BG_BASE};")

        self._pg_dash   = DashboardPage()
        self._pg_dash.set_client(self._client)
        self._pg_movies = MoviesPage(self._client)
        self._pg_movies.favorite_changed.connect(self._on_fav_changed)
        self._pg_fav    = FavoritesPage(self._client)

        self._stack.addWidget(self._pg_dash)    # 0
        self._stack.addWidget(self._pg_movies)  # 1
        self._stack.addWidget(self._pg_fav)     # 2

        rl.addWidget(self._stack)
        root.addWidget(right, stretch=1)

        self._sb = QStatusBar()
        self.setStatusBar(self._sb)
        self._update_status()

        t = QTimer(self)
        t.timeout.connect(self._update_status)
        t.start(60_000)

    def _navigate(self, idx: int):
        self._stack.setCurrentIndex(idx)
        pages = ["Dashboard", "Film Populer", "Favorit Saya"]
        self._topbar.set_page(pages[idx])
        self._sidebar.btn_dashboard.set_active(idx == 0)
        self._sidebar.btn_movies.set_active(idx == 1)
        self._sidebar.btn_favorites.set_active(idx == 2)

        if idx == 0:
            self._pg_dash.refresh(self._pg_movies._films, self._api_req)
        elif idx == 2:
            self._pg_fav.load_favorites()
            self._pg_movies.refresh_card_states()
        self._update_status()

    def _on_fav_changed(self, msg: str):
        self._sb.showMessage(f"  {msg}", 5000)
        self._api_req = self._pg_movies.api_req
        from database.db_manager import DatabaseManager
        n = DatabaseManager().count()
        self._sidebar.lbl_db.setText(f"● SQLite · {n} film favorit")
        self._sidebar.lbl_api.setText("● TMDb API · Online ✓")
        self._sidebar.lbl_api.setStyleSheet(
            f"color: {GREEN_ACT}; font-size: 10px;"
        )
        if self._stack.currentIndex() == 0:
            self._pg_dash.refresh(self._pg_movies._films, self._api_req)

    def _update_status(self):
        now = QDateTime.currentDateTime().toString("ddd, d MMM yyyy · HH:mm")
        self._sb.showMessage(
            f"  📅 {now}   ·   TMDb API v3   ·   "
            f"SQLite Lokal   ·   Python 3 · PySide6 6.x"
        )

    def closeEvent(self, e):
        """Stop semua thread sebelum jendela ditutup — cegah QThread warning."""
        self._pg_movies._cleanup()
        super().closeEvent(e)
