"""
ui/pages/favorites_page.py
Halaman FAVORIT — daftar film favorit dengan CRUD lengkap.
Kartu visual dengan poster + catatan pribadi yang bisa diedit/dihapus.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QDialog, QFormLayout,
    QTextEdit, QDoubleSpinBox, QComboBox, QDialogButtonBox,
    QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (QFont, QPixmap, QPainter, QColor,
                            QLinearGradient, QBrush, QPen, QPainterPath)

from database.db_manager import DatabaseManager
from ui.components.image_cache import get_cached, store
from ui.theme import (BG_BASE, BG_SURFACE, BG_CARD, WHITE, GRAY_100,
                       GRAY_200, GRAY_300, GRAY_400, RED, GOLD, GREEN_ACT,
                       BORDER, GENRE_COLORS)

GENRE_LIST = ["Film","Aksi","Drama","Komedi","Horor","Sci-Fi",
              "Animasi","Romantis","Thriller","Petualangan","Fantasi","Lainnya"]


class EditDialog(QDialog):
    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("✏️  Edit Film Favorit")
        self.setMinimumWidth(440)
        self.setModal(True)
        lay = QVBoxLayout(self)
        lay.setSpacing(14); lay.setContentsMargins(24,24,24,24)

        lbl = QLabel(f"✏️  {data.get('judul','?')}")
        lbl.setFont(QFont("Segoe UI",13,QFont.Bold))
        lbl.setStyleSheet(f"color:{WHITE};")
        lay.addWidget(lbl)

        sep = QFrame(); sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"border:none;border-top:1px solid {BORDER};")
        lay.addWidget(sep)

        form = QFormLayout(); form.setSpacing(10)

        self.combo = QComboBox()
        self.combo.addItems(GENRE_LIST)
        idx = self.combo.findText(data.get("genre","Film"))
        self.combo.setCurrentIndex(max(idx,0))
        form.addRow("Genre", self.combo)

        self.spin = QDoubleSpinBox()
        self.spin.setRange(0,10); self.spin.setSingleStep(0.1)
        self.spin.setDecimals(1); self.spin.setValue(float(data.get("rating",0)))
        form.addRow("Rating (0–10)", self.spin)

        self.txt = QTextEdit()
        self.txt.setPlainText(data.get("catatan",""))
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
            "genre": self.combo.currentText(),
            "rating": self.spin.value(),
            "catatan": self.txt.toPlainText().strip(),
        }


class FavCard(QFrame):
    """Kartu film favorit dengan poster thumbnail kiri dan info + aksi kanan."""
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
        self._build(data)
        self._load_poster(data)

    def _build(self, d):
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0,0,16,0)
        lay.setSpacing(0)

        # Poster kiri
        self._poster = QLabel()
        self._poster.setFixedSize(80, 120)
        self._poster.setAlignment(Qt.AlignCenter)
        self._poster.setStyleSheet(f"background: {BG_CARD}; border-radius: 10px 0 0 10px;")
        self._poster.setText("🎬")
        self._poster.setFont(QFont("Segoe UI Emoji", 20))
        lay.addWidget(self._poster)

        # Info tengah
        info = QVBoxLayout()
        info.setContentsMargins(18,14,14,14)
        info.setSpacing(5)

        lbl_j = QLabel(d.get("judul","?"))
        lbl_j.setFont(QFont("Segoe UI",12,QFont.Bold))
        lbl_j.setStyleSheet(f"color:{WHITE}; background:transparent;")

        genre = d.get("genre","Film")
        gcolor = "#E50914"
        row1 = QHBoxLayout(); row1.setSpacing(8)
        lbl_g = QLabel(genre)
        lbl_g.setStyleSheet(f"""
            color:{gcolor}; font-size:10px; font-weight:700;
            background:rgba(229,9,20,0.12); border:1px solid rgba(229,9,20,0.3);
            border-radius:4px; padding:1px 8px;
        """)
        lbl_yr = QLabel(d.get("release_year","") or "")
        lbl_yr.setStyleSheet(f"color:{GRAY_400}; font-size:10px; background:transparent;")
        lbl_dt = QLabel(f"📅 {d.get('tanggal_tambah','')}")
        lbl_dt.setStyleSheet(f"color:{GRAY_400}; font-size:10px; background:transparent;")
        row1.addWidget(lbl_g); row1.addWidget(lbl_yr); row1.addStretch(); row1.addWidget(lbl_dt)

        cat = d.get("catatan","")
        lbl_c = QLabel(f"📝 {cat[:70]}…" if len(cat)>70 else (f"📝 {cat}" if cat else "Belum ada catatan"))
        lbl_c.setStyleSheet(f"color:{GRAY_300}; font-size:11px; font-style:italic; background:transparent;")

        info.addWidget(lbl_j)
        info.addLayout(row1)
        info.addWidget(lbl_c)
        info.addStretch()
        lay.addLayout(info, stretch=1)

        # Rating + tombol kanan
        right = QVBoxLayout()
        right.setSpacing(8); right.setContentsMargins(0,14,0,14)
        right.setAlignment(Qt.AlignRight|Qt.AlignVCenter)

        rating = float(d.get("rating",0))
        rc = GREEN_ACT if rating>=8 else GOLD if rating>=6.5 else "#ff6b35" if rating>=5 else GRAY_300
        lbl_r = QLabel(f"⭐ {rating:.1f}")
        lbl_r.setFont(QFont("Consolas",15,QFont.Bold))
        lbl_r.setStyleSheet(f"color:{rc}; background:transparent;")
        lbl_r.setAlignment(Qt.AlignRight)

        btn_e = QPushButton("✏️  Edit")
        btn_e.setObjectName("btn_edit")
        btn_e.setFixedSize(88, 30)
        btn_e.clicked.connect(lambda: self.klik_edit.emit(self.fav_id))

        btn_h = QPushButton("🗑️  Hapus")
        btn_h.setObjectName("btn_danger")
        btn_h.setFixedSize(88, 30)
        btn_h.clicked.connect(lambda: self.klik_hapus.emit(self.fav_id))

        right.addWidget(lbl_r)
        right.addStretch()
        right.addWidget(btn_e)
        right.addWidget(btn_h)
        lay.addLayout(right)

    def _load_poster(self, d: dict):
        path = d.get("poster_path","")
        if not path or not self.client:
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
            scaled = px.scaled(80, 120, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            # Crop center
            x = (scaled.width() - 80) // 2
            y = (scaled.height() - 120) // 2
            cropped = scaled.copy(x, y, 80, 120)
            self._poster.setPixmap(cropped)
            self._poster.setText("")


class FavoritesPage(QWidget):
    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.db     = DatabaseManager()
        self.client = client
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0,0,0,0)
        root.setSpacing(0)

        # Header
        hdr = QFrame()
        hdr.setFixedHeight(60)
        hdr.setStyleSheet(f"background:{BG_BASE}; border-bottom:1px solid {BORDER};")
        hl = QHBoxLayout(hdr)
        hl.setContentsMargins(40,0,40,0)

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

        # Stat bar
        root.addWidget(self._build_statbar())

        # Scroll list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._list_w = QWidget()
        self._list_w.setStyleSheet(f"background:{BG_BASE};")
        self._list_lay = QVBoxLayout(self._list_w)
        self._list_lay.setContentsMargins(40,20,40,40)
        self._list_lay.setSpacing(10)
        self._list_lay.addStretch()

        scroll.setWidget(self._list_w)
        root.addWidget(scroll)

    def _build_statbar(self) -> QFrame:
        f = QFrame()
        f.setFixedHeight(44)
        f.setStyleSheet(f"background:{BG_SURFACE}; border-bottom:1px solid {BORDER};")
        lay = QHBoxLayout(f)
        lay.setContentsMargins(40,0,40,0); lay.setSpacing(32)
        self._lbl_total = QLabel("Total: 0 film")
        self._lbl_avg   = QLabel("Rating rata-rata: –")
        self._lbl_db    = QLabel("📂  cinetrack.db · SQLite Lokal")
        for l in [self._lbl_total, self._lbl_avg, self._lbl_db]:
            l.setStyleSheet(f"color:{GRAY_400}; font-size:11px;")
            lay.addWidget(l)
        lay.addStretch()
        return f

    def load_favorites(self):
        while self._list_lay.count() > 1:
            item = self._list_lay.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        semua = self.db.semua()
        if not semua:
            lbl = QLabel("🎬  Belum ada film favorit.\nTambahkan dari halaman Film Populer!")
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet(f"color:{GRAY_400}; font-size:14px; padding:80px;")
            self._list_lay.insertWidget(0, lbl)
        else:
            for d in semua:
                card = FavCard(d, self.client)
                card.klik_edit.connect(self._edit)
                card.klik_hapus.connect(self._hapus)
                self._list_lay.insertWidget(self._list_lay.count()-1, card)

        n   = len(semua)
        avg = self.db.avg_rating()
        self._lbl_count.setText(f"{n} film")
        self._lbl_total.setText(f"Total: {n} film")
        self._lbl_avg.setText(f"Rating rata-rata: {'–' if not avg else f'{avg:.1f} ⭐'}")

    def _tambah_manual(self):
        dlg = EditDialog({"judul":"","genre":"Film","rating":0,"catatan":""}, self)
        dlg.setWindowTitle("➕  Tambah Film Favorit")
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            self.db.tambah(tmdb_id=0, judul="Film Baru",
                           genre=d["genre"], rating=d["rating"],
                           catatan=d["catatan"])
            self.load_favorites()

    def _edit(self, fid: int):
        data = self.db.by_id(fid)
        if not data: return
        dlg = EditDialog(data, self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            self.db.update(fid, data.get("judul",""), d["genre"], d["rating"], d["catatan"])
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
