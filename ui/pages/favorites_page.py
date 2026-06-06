"""
ui/pages/favorites_page.py
Halaman FAVORIT — CRUD lengkap.
Setiap kartu bisa diklik untuk melihat detail + sinopsis film.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QDialog, QFormLayout,
    QTextEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox,
    QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (QFont, QPixmap, QPainter, QColor,
                            QLinearGradient, QBrush, QPen, QPainterPath,
                            QCursor)

from database.db_manager import DatabaseManager
from ui.components.image_cache import get_cached, store
from ui.theme import (BG_BASE, BG_SURFACE, BG_CARD, WHITE, GRAY_100,
                       GRAY_200, GRAY_300, GRAY_400, RED, GOLD, GREEN_ACT,
                       BORDER, GENRE_COLORS)

GENRE_LIST = ["Film","Aksi","Drama","Komedi","Horor","Sci-Fi",
              "Animasi","Romantis","Thriller","Petualangan","Fantasi","Lainnya"]


# Dialog Edit 
class EditDialog(QDialog):
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️  Edit Film Favorit")
        self.setMinimumWidth(440)
        self.setModal(True)
        lay = QVBoxLayout(self)
        lay.setSpacing(14)
        lay.setContentsMargins(24, 24, 24, 24)

        lbl = QLabel(f"✏️  {data.get('judul','?')}")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Bold))
        lbl.setStyleSheet(f"color:{WHITE};")
        lay.addWidget(lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"border:none;border-top:1px solid {BORDER};")
        lay.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(10)

        self.combo = QComboBox()
        self.combo.addItems(GENRE_LIST)
        idx = self.combo.findText(data.get("genre", "Film"))
        self.combo.setCurrentIndex(max(idx, 0))
        form.addRow("Genre", self.combo)

        self.spin = QDoubleSpinBox()
        self.spin.setRange(0, 10)
        self.spin.setSingleStep(0.1)
        self.spin.setDecimals(1)
        self.spin.setValue(float(data.get("rating", 0)))
        form.addRow("Rating (0–10)", self.spin)

        self.txt = QTextEdit()
        self.txt.setPlainText(data.get("catatan", ""))
        self.txt.setFixedHeight(90)
        self.txt.setPlaceholderText("Tulis catatan pribadi...")
        form.addRow("Catatan", self.txt)

        lay.addLayout(form)

        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def get_data(self) -> dict:
        return {
            "genre":   self.combo.currentText(),
            "rating":  self.spin.value(),
            "catatan": self.txt.toPlainText().strip(),
        }


# Dialog Detail Favorit 
class FavDetailDialog(QDialog):
    """
    Dialog detail film dari daftar favorit.
    Menampilkan: poster, sinopsis, rating, genre, catatan pribadi.
    Bisa edit catatan atau hapus langsung dari sini.
    """
    data_changed = Signal()

    def __init__(self, data: dict, db: DatabaseManager, client=None, parent=None):
        super().__init__(parent)
        self._data   = data
        self._db     = db
        self._client = client
        self._img_worker = None
        self.setWindowTitle(data.get("judul", "Detail Film"))
        self.setMinimumSize(720, 460)
        self.setModal(True)
        self._build()
        self._load_poster()

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Poster kiri ──
        self._poster_lbl = QLabel("🎬")
        self._poster_lbl.setFixedSize(220, 330)
        self._poster_lbl.setAlignment(Qt.AlignCenter)
        self._poster_lbl.setFont(QFont("Segoe UI Emoji", 36))
        self._poster_lbl.setStyleSheet(
            f"background: {BG_CARD}; border-radius: 0;"
        )
        root.addWidget(self._poster_lbl)

        # ── Info kanan ──
        right = QWidget()
        right.setStyleSheet(f"background: {BG_SURFACE};")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(28, 28, 28, 28)
        rl.setSpacing(10)

        # Judul
        lbl_j = QLabel(self._data.get("judul", "?"))
        lbl_j.setFont(QFont("Segoe UI", 17, QFont.Black))
        lbl_j.setStyleSheet(f"color:{WHITE}; background:transparent;")
        lbl_j.setWordWrap(True)
        rl.addWidget(lbl_j)

        # Meta: genre, rating, tahun
        rating = float(self._data.get("rating", 0))
        genre  = self._data.get("genre", "–")
        tahun  = self._data.get("release_year", "–") or "–"
        tgl    = self._data.get("tanggal_tambah", "–")
        lbl_m  = QLabel(
            f"⭐ {rating:.1f}  ·  {genre}  ·  {tahun}  ·  Ditambahkan: {tgl}"
        )
        lbl_m.setStyleSheet(
            f"color:{GRAY_200}; font-size:12px; background:transparent;"
        )
        rl.addWidget(lbl_m)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"border:none; border-top:1px solid {BORDER};")
        rl.addWidget(sep)

        # Sinopsis
        lbl_syn = QLabel("SINOPSIS")
        lbl_syn.setObjectName("form_label")
        rl.addWidget(lbl_syn)

        overview = self._data.get("overview", "").strip()
        if not overview:
            overview = "Sinopsis tidak tersedia untuk film ini."
        lbl_ov = QLabel(overview)
        lbl_ov.setStyleSheet(
            f"color:{GRAY_200}; font-size:12px; "
            f"line-height:1.6; background:transparent;"
        )
        lbl_ov.setWordWrap(True)
        rl.addWidget(lbl_ov)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"border:none; border-top:1px solid {BORDER};")
        rl.addWidget(sep2)

        # Catatan pribadi
        lbl_cat = QLabel("CATATAN PRIBADI")
        lbl_cat.setObjectName("form_label")
        rl.addWidget(lbl_cat)

        catatan = self._data.get("catatan", "").strip()
        self._txt = QTextEdit()
        self._txt.setFixedHeight(70)
        self._txt.setPlainText(catatan)
        self._txt.setPlaceholderText(
            "Tulis catatan atau kesan pribadi tentang film ini..."
        )
        rl.addWidget(self._txt)

        rl.addStretch()

        # Tombol aksi
        row_btn = QHBoxLayout()
        row_btn.setSpacing(10)

        btn_save = QPushButton("💾  Simpan Catatan")
        btn_save.setObjectName("btn_primary")
        btn_save.setFixedHeight(38)
        btn_save.clicked.connect(self._save)

        btn_edit = QPushButton("✏️  Edit Detail")
        btn_edit.setObjectName("btn_secondary")
        btn_edit.setFixedHeight(38)
        btn_edit.clicked.connect(self._edit)

        btn_hapus = QPushButton("🗑️  Hapus Favorit")
        btn_hapus.setObjectName("btn_danger")
        btn_hapus.setFixedHeight(38)
        btn_hapus.clicked.connect(self._hapus)

        btn_close = QPushButton("Tutup")
        btn_close.setObjectName("btn_ghost")
        btn_close.setFixedHeight(38)
        btn_close.clicked.connect(self.accept)

        row_btn.addWidget(btn_save)
        row_btn.addWidget(btn_edit)
        row_btn.addWidget(btn_hapus)
        row_btn.addStretch()
        row_btn.addWidget(btn_close)
        rl.addLayout(row_btn)

        root.addWidget(right, stretch=1)

    def _load_poster(self):
        if not self._client:
            return
        path = self._data.get("poster_path", "")
        if not path:
            return
        url = self._client.poster_url(path, "w500")
        if not url:
            return
        px = get_cached(url)
        if px:
            self._set_poster(px)
            return
        from api.workers import ImageWorker
        self._img_worker = ImageWorker(self._client, url)
        self._img_worker.finished.connect(
            lambda u, d: self._set_poster(store(u, d))
        )
        self._img_worker.start()

    def _set_poster(self, px: QPixmap):
        if px and not px.isNull():
            scaled = px.scaled(
                220, 330, Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (scaled.width()  - 220) // 2
            y = (scaled.height() - 330) // 2
            self._poster_lbl.setPixmap(scaled.copy(x, y, 220, 330))
            self._poster_lbl.setText("")

    def _save(self):
        catatan = self._txt.toPlainText().strip()
        self._db.update(
            self._data["id"],
            self._data.get("judul", ""),
            self._data.get("genre", ""),
            float(self._data.get("rating", 0)),
            catatan,
        )
        QMessageBox.information(self, "Tersimpan", "Catatan berhasil disimpan! 💾")
        self.data_changed.emit()

    def _edit(self):
        dlg = EditDialog(self._data, self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            self._db.update(
                self._data["id"],
                self._data.get("judul", ""),
                d["genre"],
                d["rating"],
                d["catatan"],
            )
            self.data_changed.emit()
            self.accept()

    def _hapus(self):
        box = QMessageBox(self)
        box.setWindowTitle("🗑️  Hapus Favorit?")
        box.setIcon(QMessageBox.Question)
        box.setText(
            f"Hapus <b>{self._data.get('judul','film ini')}</b> "
            f"dari daftar favorit?"
        )
        box.setInformativeText("Tindakan ini tidak dapat dibatalkan.")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        if box.exec() == QMessageBox.Yes:
            self._db.hapus(self._data["id"])
            self.data_changed.emit()
            self.accept()

    def closeEvent(self, e):
        if self._img_worker and self._img_worker.isRunning():
            self._img_worker.stop()
        super().closeEvent(e)


# ── FavCard ───────────────────────────────────────────────────────
class FavCard(QFrame):
    klik_card  = Signal(dict)   # klik area utama → buka detail
    klik_edit  = Signal(int)
    klik_hapus = Signal(int)

    def __init__(self, data: dict, client=None, parent=None):
        super().__init__(parent)
        self.fav_id = data["id"]
        self.data   = data
        self.client = client
        self.setObjectName("fav_card")
        self.setFixedHeight(120)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self._build(data)
        self._load_poster(data)

    def _build(self, d):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 16, 0)
        lay.setSpacing(0)

        # Poster thumbnail kiri
        self._poster = QLabel()
        self._poster.setFixedSize(80, 120)
        self._poster.setAlignment(Qt.AlignCenter)
        self._poster.setStyleSheet(
            f"background: {BG_CARD}; border-radius: 10px 0 0 10px;"
        )
        self._poster.setText("🎬")
        self._poster.setFont(QFont("Segoe UI Emoji", 22))
        lay.addWidget(self._poster)

        # Info tengah
        info = QVBoxLayout()
        info.setContentsMargins(18, 14, 14, 14)
        info.setSpacing(5)

        lbl_j = QLabel(d.get("judul", "?"))
        lbl_j.setFont(QFont("Segoe UI", 12, QFont.Bold))
        lbl_j.setStyleSheet(f"color:{WHITE}; background:transparent;")

        genre = d.get("genre", "Film")
        row1  = QHBoxLayout()
        row1.setSpacing(8)
        lbl_g = QLabel(genre)
        lbl_g.setStyleSheet(f"""
            color:{RED}; font-size:10px; font-weight:700;
            background:rgba(229,9,20,0.12);
            border:1px solid rgba(229,9,20,0.3);
            border-radius:4px; padding:1px 8px;
        """)
        lbl_yr = QLabel(d.get("release_year", "") or "")
        lbl_yr.setStyleSheet(
            f"color:{GRAY_400}; font-size:10px; background:transparent;"
        )
        lbl_dt = QLabel(f"📅 {d.get('tanggal_tambah','')}")
        lbl_dt.setStyleSheet(
            f"color:{GRAY_400}; font-size:10px; background:transparent;"
        )
        row1.addWidget(lbl_g)
        row1.addWidget(lbl_yr)
        row1.addStretch()
        row1.addWidget(lbl_dt)

        # Sinopsis ringkas
        overview = d.get("overview", "").strip()
        if not overview:
            overview = "Klik untuk melihat detail film."
        preview = overview[:80] + "…" if len(overview) > 80 else overview
        lbl_ov = QLabel(preview)
        lbl_ov.setStyleSheet(
            f"color:{GRAY_300}; font-size:11px; "
            f"font-style:italic; background:transparent;"
        )

        info.addWidget(lbl_j)
        info.addLayout(row1)
        info.addWidget(lbl_ov)
        info.addStretch()
        lay.addLayout(info, stretch=1)

        # Rating + tombol kanan
        right = QVBoxLayout()
        right.setSpacing(8)
        right.setContentsMargins(0, 14, 0, 14)
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        rating = float(d.get("rating", 0))
        rc = (GREEN_ACT if rating >= 8 else
              GOLD if rating >= 6.5 else
              "#ff6b35" if rating >= 5 else GRAY_300)
        lbl_r = QLabel(f"⭐ {rating:.1f}")
        lbl_r.setFont(QFont("Consolas", 15, QFont.Bold))
        lbl_r.setStyleSheet(f"color:{rc}; background:transparent;")
        lbl_r.setAlignment(Qt.AlignRight)

        btn_e = QPushButton("✏️  Edit")
        btn_e.setObjectName("btn_edit")
        btn_e.setFixedSize(88, 30)
        btn_e.setCursor(QCursor(Qt.PointingHandCursor))
        btn_e.clicked.connect(lambda: self.klik_edit.emit(self.fav_id))

        btn_h = QPushButton("🗑️  Hapus")
        btn_h.setObjectName("btn_danger")
        btn_h.setFixedSize(88, 30)
        btn_h.setCursor(QCursor(Qt.PointingHandCursor))
        btn_h.clicked.connect(lambda: self.klik_hapus.emit(self.fav_id))

        right.addWidget(lbl_r)
        right.addStretch()
        right.addWidget(btn_e)
        right.addWidget(btn_h)
        lay.addLayout(right)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.klik_card.emit(self.data)

    def _load_poster(self, d: dict):
        if not self.client:
            return
        path = d.get("poster_path", "")
        if not path:
            return
        url = self.client.poster_url(path, "w500")
        if not url:
            return
        px = get_cached(url)
        if px:
            self._set_poster(px)
            return
        from api.workers import ImageWorker
        w = ImageWorker(self.client, url)
        w.finished.connect(lambda u, data: self._set_poster(store(u, data)))
        w.start()
        self._img_w = w

    def _set_poster(self, px: QPixmap):
        if px and not px.isNull():
            scaled = px.scaled(
                80, 120, Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            x = (scaled.width()  - 80)  // 2
            y = (scaled.height() - 120) // 2
            self._poster.setPixmap(scaled.copy(x, y, 80, 120))
            self._poster.setText("")


# ── FavoritesPage ─────────────────────────────────────────────────
class FavoritesPage(QWidget):
    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.db     = DatabaseManager()
        self.client = client
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setFixedHeight(60)
        hdr.setStyleSheet(
            f"background:{BG_BASE}; border-bottom:1px solid {BORDER};"
        )
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(40, 0, 40, 0)

        lbl_t = QLabel("Favorit Saya")
        lbl_t.setObjectName("page_title")
        self._lbl_count = QLabel("")
        self._lbl_count.setObjectName("muted")

        btn_add = QPushButton("➕  Tambah Manual")
        btn_add.setObjectName("btn_ghost")
        btn_add.setFixedHeight(36)
        btn_add.clicked.connect(self._tambah_manual)

        hl.addWidget(lbl_t)
        hl.addSpacing(12)
        hl.addWidget(self._lbl_count)
        hl.addStretch()
        hl.addWidget(btn_add)
        root.addWidget(hdr)

        root.addWidget(self._build_statbar())

        # Hint klik
        hint = QLabel(
            "💡  Klik kartu film untuk melihat sinopsis dan detail lengkap"
        )
        hint.setStyleSheet(
            f"color:{GRAY_400}; font-size:11px; "
            f"padding:8px 40px; background:{BG_SURFACE}; "
            f"border-bottom:1px solid {BORDER};"
        )
        root.addWidget(hint)

        # Scroll list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._list_w = QWidget()
        self._list_w.setStyleSheet(f"background:{BG_BASE};")
        self._list_lay = QVBoxLayout(self._list_w)
        self._list_lay.setContentsMargins(40, 20, 40, 40)
        self._list_lay.setSpacing(10)
        self._list_lay.addStretch()

        scroll.setWidget(self._list_w)
        root.addWidget(scroll)

    def _build_statbar(self) -> QFrame:
        f = QFrame()
        f.setFixedHeight(44)
        f.setStyleSheet(
            f"background:{BG_SURFACE}; border-bottom:1px solid {BORDER};"
        )
        lay = QHBoxLayout(f)
        lay.setContentsMargins(40, 0, 40, 0)
        lay.setSpacing(32)
        self._lbl_total = QLabel("Total: 0 film")
        self._lbl_avg   = QLabel("Rating rata-rata: –")
        self._lbl_db    = QLabel("📂  cinetrack.db · SQLite Lokal")
        for l in [self._lbl_total, self._lbl_avg, self._lbl_db]:
            l.setStyleSheet(f"color:{GRAY_400}; font-size:11px;")
            lay.addWidget(l)
        lay.addStretch()
        return f

    # ── CRUD ─────────────────────────────────────────────────────

    def load_favorites(self):
        # Bersihkan list lama
        while self._list_lay.count() > 1:
            item = self._list_lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        semua = self.db.semua()
        if not semua:
            lbl = QLabel(
                "🎬  Belum ada film favorit.\n"
                "Tambahkan dari halaman Film Populer!"
            )
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(
                f"color:{GRAY_400}; font-size:14px; padding:80px;"
            )
            self._list_lay.insertWidget(0, lbl)
        else:
            for d in semua:
                card = FavCard(d, self.client)
                card.klik_card.connect(self._show_detail)
                card.klik_edit.connect(self._edit)
                card.klik_hapus.connect(self._hapus)
                self._list_lay.insertWidget(
                    self._list_lay.count() - 1, card
                )

        n   = len(semua)
        avg = self.db.avg_rating()
        self._lbl_count.setText(f"{n} film")
        self._lbl_total.setText(f"Total: {n} film")
        self._lbl_avg.setText(
            f"Rating rata-rata: {'–' if not avg else f'{avg:.1f} ⭐'}"
        )

    def _show_detail(self, data: dict):
        """Buka dialog detail dengan sinopsis + catatan."""
        dlg = FavDetailDialog(data, self.db, self.client, self)
        dlg.data_changed.connect(self.load_favorites)
        dlg.exec()

    def _tambah_manual(self):
        dlg = EditDialog(
            {"judul":"","genre":"Film","rating":0,"catatan":""}, self
        )
        dlg.setWindowTitle("➕  Tambah Film Favorit")
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            self.db.tambah(
                tmdb_id=0, judul="Film Baru",
                genre=d["genre"], rating=d["rating"],
                catatan=d["catatan"]
            )
            self.load_favorites()

    def _edit(self, fid: int):
        data = self.db.by_id(fid)
        if not data:
            return
        dlg = EditDialog(data, self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            self.db.update(
                fid, data.get("judul",""),
                d["genre"], d["rating"], d["catatan"]
            )
            self.load_favorites()

    def _hapus(self, fid: int):
        d = self.db.by_id(fid)
        j = d.get("judul","film ini") if d else "film ini"
        box = QMessageBox(self)
        box.setWindowTitle("🗑️  Hapus Favorit?")
        box.setIcon(QMessageBox.Question)
        box.setText(f"Hapus <b>{j}</b> dari daftar favorit?")
        box.setInformativeText("Tindakan ini tidak dapat dibatalkan.")
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        if box.exec() == QMessageBox.Yes:
            self.db.hapus(fid)
            self.load_favorites()

    def showEvent(self, e):
        super().showEvent(e)
        self.load_favorites()
