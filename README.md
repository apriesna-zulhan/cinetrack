# 🎬 CineTrack v2 — Katalog Film Desktop

Aplikasi desktop katalog film berbasis **PySide6**, data film dari **TMDb API v3**, penyimpanan lokal **SQLite**.

## Anggota Kelompok

| Nama | NIM | Modul |
|------|-----|-------|
| Anggota 1 | F1D023XXXXX | Backend: `config.py`, `api/`, `database/` |
| Anggota 2 | F1D023XXXXX | UI Core: `main.py`, `ui/theme.py`, `ui/main_window.py`, `ui/components/` |
| Anggota 3 | F1D023XXXXX | Halaman: `ui/pages/` |

> **Ganti nama dan NIM** di tabel di atas dan di `ui/main_window.py` → variabel `ANGGOTA`.

## Fitur

- **3 Halaman**: Dashboard (chart), Film Populer (grid + hero), Favorit Saya (CRUD)
- **Navigasi**: Sidebar + `QStackedWidget` + Menu Bar (File / Export / Help)
- **Pencarian & Filter**: Search judul + filter genre (chips) di Film Populer; search + sort di Favorit
- **Export**: CSV dan PDF (via ReportLab, fallback HTML) dari halaman Favorit
- **Visualisasi**: Bar chart Top 10 popularitas (QtCharts)
- **Multithreading**: QThread workers untuk fetch API dan download gambar paralel
- **Database**: SQLite 2 tabel (`favorit` + `riwayat`) dengan relasi foreign key
- **Validasi**: Semua form divalidasi — field kosong, format, panjang karakter
- **Styling**: Netflix dark theme via `setStyleSheet()` global (QSS)
- **Status Bar**: Nama & NIM semua anggota (tidak dapat diedit)

## Instalasi & Jalankan

```bash
pip install -r requirements.txt
python main.py
```

### Dependensi opsional (untuk export PDF):
```bash
pip install reportlab
```
Jika `reportlab` tidak terinstal, export PDF otomatis menggunakan fallback HTML.

## Struktur Folder

```
CineTrack/
├── main.py               # Entry point
├── config.py             # Konfigurasi (API key, URL)
├── requirements.txt
├── README.md
├── api/
│   ├── tmdb_client.py    # TMDb REST API client
│   └── workers.py        # QThread workers
├── database/
│   └── db_manager.py     # SQLite CRUD (tabel: favorit, riwayat)
├── utils/
│   └── export.py         # Export CSV & PDF
└── ui/
    ├── theme.py           # Netflix dark theme + QSS
    ├── main_window.py     # Jendela utama + sidebar + menu bar
    ├── pages/
    │   ├── dashboard_page.py   # Statistik + chart
    │   ├── movies_page.py      # Grid film + hero + detail
    │   └── favorites_page.py   # CRUD + search + sort + export
    └── components/
        ├── movie_card.py
        ├── hero_banner.py
        ├── image_cache.py
        └── stat_card.py
```

## Catatan

- File `cinetrack.db` dan folder `__pycache__/` tidak perlu di-push ke GitHub (sudah di `.gitignore`)
- API Key TMDb ada di `config.py` — ganti jika expired
