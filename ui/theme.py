"""
ui/theme.py — Netflix Dark Theme
Semua warna, font, dan QSS terpusat di sini.
"""

BG_BASE    = "#141414"
BG_SURFACE = "#1F1F1F"
BG_CARD    = "#2A2A2A"
BG_HOVER   = "#333333"
BG_INPUT   = "#242424"

RED        = "#E50914"
RED_HOVER  = "#F40612"
RED_DIM    = "#B20710"

WHITE      = "#FFFFFF"
GRAY_100   = "#E5E5E5"
GRAY_200   = "#B3B3B3"
GRAY_300   = "#808080"
GRAY_400   = "#4A4A4A"
GRAY_500   = "#2A2A2A"

GOLD       = "#F5C518"
GREEN_ACT  = "#46D369"
BLUE_ACT   = "#0071EB"

BORDER     = "#2A2A2A"

GENRE_COLORS = {
    28:"#E50914", 18:"#6B46C1", 35:"#D97706", 27:"#DC2626",
    878:"#2563EB", 16:"#059669", 10749:"#DB2777", 53:"#7C3AED",
    99:"#374151", 12:"#B45309", 14:"#4F46E5", 80:"#991B1B",
    36:"#78350F", 10751:"#0369A1", 10402:"#065F46", 9648:"#1E3A5F",
}
GENRE_NAMES = {
    28:"Aksi", 18:"Drama", 35:"Komedi", 27:"Horor", 878:"Sci-Fi",
    16:"Animasi", 10749:"Romantis", 53:"Thriller", 99:"Dokumenter",
    12:"Petualangan", 14:"Fantasi", 80:"Kriminal", 36:"Sejarah",
    10751:"Keluarga", 10402:"Musik", 9648:"Misteri",
}

QSS = f"""
* {{
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: {GRAY_100};
    background-color: transparent;
    border: none;
    outline: none;
}}
QMainWindow, QDialog {{ background-color: {BG_BASE}; }}
QWidget#root_widget {{ background-color: {BG_BASE}; }}

QFrame#sidebar {{
    background-color: #0D0D0D;
    border-right: 1px solid {BORDER};
}}
QLabel#logo_text {{
    color: {RED};
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 3px;
}}
QLabel#nav_section {{
    color: {GRAY_300};
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    padding: 0 20px;
}}
QPushButton#nav_btn {{
    background: transparent;
    color: {GRAY_300};
    border: none;
    border-left: 3px solid transparent;
    border-radius: 0;
    text-align: left;
    padding: 12px 20px;
    font-size: 13px;
}}
QPushButton#nav_btn:hover {{
    background: rgba(255,255,255,0.06);
    color: {WHITE};
    border-left: 3px solid {GRAY_400};
}}
QPushButton#nav_btn[active=true] {{
    background: rgba(229,9,20,0.1);
    color: {WHITE};
    border-left: 3px solid {RED};
    font-weight: 700;
}}

QFrame#topbar {{ background-color: {BG_BASE}; border-bottom: 1px solid {BORDER}; }}
QLineEdit#search_input {{
    background: {BG_SURFACE};
    color: {WHITE};
    border: 1.5px solid {BORDER};
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 13px;
    selection-background-color: {RED};
}}
QLineEdit#search_input:focus {{ border-color: {GRAY_300}; background: {BG_CARD}; }}

QPushButton#btn_primary {{
    background-color: {RED};
    color: {WHITE};
    border: none;
    border-radius: 5px;
    padding: 9px 22px;
    font-size: 13px;
    font-weight: 700;
}}
QPushButton#btn_primary:hover {{ background-color: {RED_HOVER}; }}
QPushButton#btn_primary:pressed {{ background-color: {RED_DIM}; }}

QPushButton#btn_secondary {{
    background-color: rgba(255,255,255,0.15);
    color: {WHITE};
    border: none;
    border-radius: 5px;
    padding: 9px 22px;
    font-size: 13px;
    font-weight: 600;
}}
QPushButton#btn_secondary:hover {{ background-color: rgba(255,255,255,0.25); }}

QPushButton#btn_ghost {{
    background: transparent;
    color: {GRAY_200};
    border: 1px solid {GRAY_400};
    border-radius: 5px;
    padding: 7px 16px;
    font-size: 12px;
}}
QPushButton#btn_ghost:hover {{ border-color: {WHITE}; color: {WHITE}; }}

QPushButton#btn_danger {{
    background: rgba(229,9,20,0.12);
    color: {RED};
    border: 1px solid rgba(229,9,20,0.35);
    border-radius: 5px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 600;
}}
QPushButton#btn_danger:hover {{ background: rgba(229,9,20,0.25); }}

QPushButton#btn_edit {{
    background: rgba(255,255,255,0.07);
    color: {GRAY_100};
    border: 1px solid {GRAY_400};
    border-radius: 5px;
    padding: 7px 14px;
    font-size: 12px;
}}
QPushButton#btn_edit:hover {{ background: rgba(255,255,255,0.14); color: {WHITE}; }}

QPushButton#genre_chip {{
    background: transparent;
    color: {GRAY_200};
    border: 1px solid {GRAY_400};
    border-radius: 20px;
    padding: 6px 18px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#genre_chip:hover {{ border-color: {WHITE}; color: {WHITE}; }}
QPushButton#genre_chip[active=true] {{
    background: {RED};
    color: {WHITE};
    border-color: {RED};
    font-weight: 700;
}}

QPushButton#load_more_btn {{
    background: transparent;
    color: {GRAY_200};
    border: 1px solid {GRAY_400};
    border-radius: 4px;
    padding: 10px 36px;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 1px;
}}
QPushButton#load_more_btn:hover {{ border-color: {WHITE}; color: {WHITE}; }}

QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}
QScrollBar:vertical {{ background: transparent; width: 4px; margin: 0; }}
QScrollBar::handle:vertical {{ background: {GRAY_400}; border-radius: 2px; min-height: 40px; }}
QScrollBar::handle:vertical:hover {{ background: {GRAY_300}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{ height: 0; }}

QLineEdit, QTextEdit, QDoubleSpinBox, QComboBox {{
    background: {BG_INPUT};
    color: {WHITE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    selection-background-color: {RED};
}}
QLineEdit:focus, QTextEdit:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border-color: {GRAY_300};
}}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
    background: {GRAY_500}; border: none; width: 16px;
}}
QComboBox::drop-down {{ border: none; width: 24px; }}
QComboBox QAbstractItemView {{
    background: {BG_SURFACE}; color: {WHITE};
    border: 1px solid {BORDER}; selection-background-color: {RED}; padding: 4px;
}}

QLabel#page_title {{ color: {WHITE}; font-size: 26px; font-weight: 800; }}
QLabel#section_title {{ color: {WHITE}; font-size: 17px; font-weight: 700; }}
QLabel#muted {{ color: {GRAY_300}; font-size: 11px; }}
QLabel#form_label {{ color: {GRAY_200}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; }}

QFrame#stat_card {{ background: {BG_SURFACE}; border: 1px solid {BORDER}; border-radius: 10px; }}
QFrame#chart_frame {{ background: {BG_SURFACE}; border: 1px solid {BORDER}; border-radius: 12px; }}
QFrame#fav_card {{ background: {BG_SURFACE}; border: 1px solid {BORDER}; border-radius: 10px; }}
QFrame#fav_card:hover {{ border-color: {GRAY_400}; background: {BG_CARD}; }}
QFrame#detail_panel {{ background: {BG_SURFACE}; border: 1px solid {BORDER}; border-radius: 12px; }}

QDialog {{ background: {BG_SURFACE}; }}
QDialogButtonBox QPushButton {{
    background: {BG_CARD}; color: {GRAY_100};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 7px 20px; min-width: 80px; font-weight: 500;
}}
QDialogButtonBox QPushButton:default {{
    background: {RED}; color: {WHITE}; border: none; font-weight: 700;
}}
QDialogButtonBox QPushButton:hover {{ background: {RED}; color: {WHITE}; border: none; }}

QMessageBox {{ background: {BG_SURFACE}; }}
QMessageBox QLabel {{ color: {WHITE}; font-size: 13px; }}
QMessageBox QPushButton {{
    background: {BG_CARD}; color: {GRAY_100};
    border: 1px solid {BORDER}; border-radius: 6px;
    padding: 7px 20px; min-width: 80px;
}}
QMessageBox QPushButton:default {{
    background: {RED}; color: {WHITE}; border: none; font-weight: 700;
}}

QProgressBar {{
    background: {BORDER}; border: none; border-radius: 2px;
}}
QProgressBar::chunk {{ background: {RED}; border-radius: 2px; }}

QStatusBar {{
    background: #0D0D0D; color: {GRAY_400};
    font-size: 10px; border-top: 1px solid {BORDER};
}}
QToolTip {{
    background: {BG_CARD}; color: {WHITE};
    border: 1px solid {BORDER}; border-radius: 4px;
    padding: 5px 10px; font-size: 11px;
}}
"""
