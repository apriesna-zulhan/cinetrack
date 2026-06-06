"""
database/db_manager.py — SQLite CRUD Manager
Menyimpan film favorit dan catatan pribadi pengguna secara lokal.
"""
import sqlite3
from typing import Optional

DB_PATH = "cinetrack.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS favorit (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    tmdb_id        INTEGER UNIQUE,
    judul          TEXT NOT NULL,
    genre          TEXT DEFAULT '',
    rating         REAL DEFAULT 0.0,
    catatan        TEXT DEFAULT '',
    poster_path    TEXT DEFAULT '',
    backdrop_path  TEXT DEFAULT '',
    overview       TEXT DEFAULT '',
    release_year   TEXT DEFAULT '',
    tanggal_tambah TEXT DEFAULT (date('now'))
);
"""


class DatabaseManager:
    def __init__(self, path: str = DB_PATH):
        self.path = path
        with self._conn() as c:
            c.execute(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    # CREATE 
    def tambah(self, tmdb_id: int, judul: str, genre: str = "",
                rating: float = 0.0, catatan: str = "",
                poster_path: str = "", backdrop_path: str = "",
                overview: str = "", release_year: str = "") -> int:
        sql = """INSERT OR REPLACE INTO favorit
                 (tmdb_id,judul,genre,rating,catatan,poster_path,backdrop_path,overview,release_year)
                 VALUES (?,?,?,?,?,?,?,?,?)"""
        with self._conn() as c:
            cur = c.execute(sql, (tmdb_id, judul, genre, rating, catatan,
                                  poster_path, backdrop_path, overview, release_year))
            return cur.lastrowid

    # READ 
    def semua(self) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM favorit ORDER BY id DESC")]

    def by_id(self, fid: int) -> Optional[dict]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM favorit WHERE id=?", (fid,)).fetchone()
            return dict(r) if r else None

    def by_tmdb(self, tmdb_id: int) -> Optional[dict]:
        with self._conn() as c:
            r = c.execute("SELECT * FROM favorit WHERE tmdb_id=?", (tmdb_id,)).fetchone()
            return dict(r) if r else None

    def tmdb_ids(self) -> set[int]:
        with self._conn() as c:
            rows = c.execute("SELECT tmdb_id FROM favorit").fetchall()
            return {r[0] for r in rows}

    def count(self) -> int:
        with self._conn() as c:
            return c.execute("SELECT COUNT(*) FROM favorit").fetchone()[0]

    def avg_rating(self) -> float:
        with self._conn() as c:
            v = c.execute("SELECT AVG(rating) FROM favorit WHERE rating>0").fetchone()[0]
            return round(v, 1) if v else 0.0

    # UPDATE 
    def update(self, fid: int, judul: str, genre: str,
               rating: float, catatan: str) -> bool:
        sql = "UPDATE favorit SET judul=?,genre=?,rating=?,catatan=? WHERE id=?"
        with self._conn() as c:
            return c.execute(sql, (judul, genre, rating, catatan, fid)).rowcount > 0

    # ── DELETE ──────────────────────────────────────────────────────
    def hapus(self, fid: int) -> bool:
        with self._conn() as c:
            return c.execute("DELETE FROM favorit WHERE id=?", (fid,)).rowcount > 0

    def hapus_by_tmdb(self, tmdb_id: int) -> bool:
        with self._conn() as c:
            return c.execute("DELETE FROM favorit WHERE tmdb_id=?", (tmdb_id,)).rowcount > 0
