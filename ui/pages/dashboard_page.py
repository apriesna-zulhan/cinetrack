"""
ui/pages/dashboard_page.py
Halaman DASHBOARD: statistik ringkas + bar chart Top 10 popularitas.
Dipisah dari halaman Film Populer sesuai navigasi modular.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtCharts import (
    QChart, QChartView, QBarSeries, QBarSet,
    QValueAxis, QBarCategoryAxis
)
from PySide6.QtGui import QPainter, QPen

from ui.components.stat_card import StatCard
from ui.theme import (BG_BASE, BG_SURFACE, BG_CARD, WHITE, GRAY_100,
                       GRAY_200, GRAY_300, GRAY_400, RED, GOLD, GREEN_ACT, BLUE_ACT, BORDER)
from database.db_manager import DatabaseManager


class DashboardPage(QWidget):
    """
    Halaman Dashboard menampilkan:
    1. Grid 4 StatCard (total film, favorit, avg rating, request API)
    2. Bar chart QtCharts Top 10 film terpopuler
    3. Ringkasan daftar favorit terbaru
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseManager()
        self._film_populer: list[dict] = []
        self._api_req = 0
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        page = QWidget()
        page.setStyleSheet(f"background: {BG_BASE};")
        lay = QVBoxLayout(page)
        lay.setContentsMargins(40, 32, 40, 40)
        lay.setSpacing(28)

        # Judul halaman
        lbl_title = QLabel("Dashboard")
        lbl_title.setObjectName("page_title")
        lay.addWidget(lbl_title)

        # ── Stats row ──
        lay.addLayout(self._build_stats())

        # ── Chart ──
        lay.addWidget(self._build_chart())

        # ── Favorit terbaru ──
        lay.addWidget(self._build_recent_fav())

        lay.addStretch()
        scroll.setWidget(page)
        root.addWidget(scroll)

    def _build_stats(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(16)
        items = [
            ("Film Populer TMDb", "–",     "Dimuat dari API",      RED),
            ("Film Favorit",      "0",     "Tersimpan di SQLite",  "#7C3AED"),
            ("Rating Rata-rata",  "–",     "Dari daftar favorit",  GOLD),
            ("Request API",       "0",     "Sesi ini",             BLUE_ACT),
        ]
        self._stats: list[StatCard] = []
        for lbl, val, sub, clr in items:
            c = StatCard(lbl, val, sub, clr)
            self._stats.append(c)
            row.addWidget(c)
        return row

    def _build_chart(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("chart_frame")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(8)

        lbl = QLabel("📊  Top 10 Film Paling Populer")
        lbl.setObjectName("section_title")
        sub = QLabel("Skor popularitas real-time dari TMDb API")
        sub.setObjectName("muted")
        lay.addWidget(lbl)
        lay.addWidget(sub)

        self._chart = QChart()
        self._chart.setBackgroundBrush(QColor(BG_SURFACE))
        self._chart.setPlotAreaBackgroundBrush(QColor(BG_SURFACE))
        self._chart.setPlotAreaBackgroundVisible(True)
        self._chart.legend().hide()
        self._chart.setAnimationOptions(QChart.SeriesAnimations)
        from PySide6.QtCore import QMargins
        self._chart.setMargins(QMargins(0, 0, 0, 0))

        self._chart_view = QChartView(self._chart)
        self._chart_view.setRenderHint(QPainter.Antialiasing)
        self._chart_view.setStyleSheet("background: transparent; border: none;")
        self._chart_view.setFixedHeight(240)
        lay.addWidget(self._chart_view)
        return frame

    def _build_recent_fav(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("chart_frame")
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("❤️  Favorit Terbaru")
        lbl.setObjectName("section_title")
        lay.addWidget(lbl)

        self._fav_preview_lay = QVBoxLayout()
        self._fav_preview_lay.setSpacing(8)
        lay.addLayout(self._fav_preview_lay)

        self._lbl_no_fav = QLabel("Belum ada film favorit. Tambahkan dari halaman Film Populer!")
        self._lbl_no_fav.setObjectName("muted")
        self._lbl_no_fav.setAlignment(Qt.AlignCenter)
        self._lbl_no_fav.setStyleSheet(f"padding: 20px; color: {GRAY_400};")
        lay.addWidget(self._lbl_no_fav)
        return frame

    # ── Public: dipanggil dari MainWindow ───────────────────────────

    def refresh(self, film_list: list[dict] = None, api_req: int = 0):
        """Perbarui semua widget dashboard."""
        if film_list is not None:
            self._film_populer = film_list
        self._api_req = api_req
        self._update_stats()
        self._update_chart()
        self._update_recent_fav()

    def _update_stats(self):
        n   = self.db.count()
        avg = self.db.avg_rating()
        self._stats[0].set_value(str(len(self._film_populer)) if self._film_populer else "–")
        self._stats[1].set_value(n)
        self._stats[2].set_value(f"{avg:.1f}" if avg else "–")
        self._stats[3].set_value(self._api_req)

    def _update_chart(self):
        self._chart.removeAllSeries()
        for ax in self._chart.axes():
            self._chart.removeAxis(ax)

        if not self._film_populer:
            return

        top10 = self._film_populer[:10]
        bs    = QBarSet("Popularitas")
        bs.setColor(QColor(RED))
        bs.setBorderColor(QColor(RED))
        cats  = []
        for f in top10:
            bs.append(round(f.get("popularity", 0), 1))
            t = f.get("title", "?")
            cats.append(t[:11] + "…" if len(t) > 11 else t)

        series = QBarSeries()
        series.append(bs)
        self._chart.addSeries(series)

        ax_x = QBarCategoryAxis()
        ax_x.append(cats)
        ax_x.setLabelsColor(QColor(GRAY_300))
        ax_x.setLabelsFont(QFont("Segoe UI", 7))
        ax_x.setGridLineVisible(False)
        ax_x.setLinePen(QPen(QColor(BORDER)))
        self._chart.addAxis(ax_x, Qt.AlignBottom)
        series.attachAxis(ax_x)

        ax_y = QValueAxis()
        ax_y.setLabelsColor(QColor(GRAY_300))
        ax_y.setLabelsFont(QFont("Segoe UI", 8))
        ax_y.setGridLineColor(QColor(BORDER))
        ax_y.setLinePen(QPen(QColor(BORDER)))
        self._chart.addAxis(ax_y, Qt.AlignLeft)
        series.attachAxis(ax_y)

    def _update_recent_fav(self):
        # Bersihkan widget lama
        while self._fav_preview_lay.count():
            item = self._fav_preview_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        favs = self.db.semua()[:5]
        if not favs:
            self._lbl_no_fav.show()
            return
        self._lbl_no_fav.hide()

        for f in favs:
            row = QFrame()
            row.setFixedHeight(44)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            lbl_j = QLabel(f.get("judul","?"))
            lbl_j.setStyleSheet(f"color: {WHITE}; font-weight: 600; font-size: 12px;")
            lbl_g = QLabel(f.get("genre",""))
            lbl_g.setStyleSheet(f"color: {GRAY_300}; font-size: 11px;")
            lbl_r = QLabel(f"⭐ {float(f.get('rating',0)):.1f}")
            lbl_r.setStyleSheet(f"color: {GOLD}; font-size: 11px; font-weight: 600;")
            lbl_d = QLabel(f.get("tanggal_tambah",""))
            lbl_d.setStyleSheet(f"color: {GRAY_400}; font-size: 10px;")
            rl.addWidget(lbl_j, stretch=3)
            rl.addWidget(lbl_g, stretch=2)
            rl.addWidget(lbl_r)
            rl.addSpacing(16)
            rl.addWidget(lbl_d)
            self._fav_preview_lay.addWidget(row)
