"""
main.py
=======
TMK Genocide Risk Framework — GUI Dashboard (PyQt6)
QStackedWidget navigasi:
  0 → Overview & Statistik
  1 → Tabel Episode (filter + pagination + badge)
  2 → Grafik A* & ACO

Cara jalankan:
    python main.py
    python main.py --events path/to/events.xls --annual path/to/annual.xlsx
"""

import sys
import argparse
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QSizePolicy, QHBoxLayout, QVBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QFrame, QScrollArea,
    QGridLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QCursor, QColor

import os
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)

from utils.algorithm import TMKFramework, EpisodeResult, TIER_ORDER
from components import (
    Typography, Button, Colors,
    VBox, HBox,
    PaginationTable,
    LineChart, ScatterPlot, BarChart,
)
from utils import Fonts


# ═══════════════════════════════════════════════════════════════════════════
# KONSTANTA WARNA RISK
# ═══════════════════════════════════════════════════════════════════════════

RISK_FG = {
    "CRITICAL": "#991B1B",
    "HIGH":     "#92400E",
    "MEDIUM":   "#1E40AF",
    "LOW":      "#166534",
}
RISK_BG = {
    "CRITICAL": "#FEE2E2",
    "HIGH":     "#FEF3C7",
    "MEDIUM":   "#DBEAFE",
    "LOW":      "#DCFCE7",
}
CONTAGION_FG = {"HOT": "#991B1B", "WARM": "#92400E", "COOL": "#166534"}
CONTAGION_BG = {"HOT": "#FEE2E2", "WARM": "#FEF3C7", "COOL": "#DCFCE7"}

NAV_ITEMS  = ["Overview", "Tabel Episode", "Grafik"]
WIN_W      = 1200
WIN_H      = 800
SIDEBAR_W  = 186

# ── Scrollbar style global ───────────────────────────────────────────────
SCROLLBAR_QSS = f"""
    QScrollBar:vertical {{
        background: {Colors.neutral_20};
        width: 7px;
        margin: 0;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical {{
        background: {Colors.neutral_40};
        min-height: 32px;
        border-radius: 3px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {Colors.neutral_50};
    }}
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar:horizontal {{
        background: {Colors.neutral_20};
        height: 7px;
        margin: 0;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal {{
        background: {Colors.neutral_40};
        min-width: 32px;
        border-radius: 3px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: {Colors.neutral_50};
    }}
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
"""


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ═══════════════════════════════════════════════════════════════════════════
# WORKER THREAD
# ═══════════════════════════════════════════════════════════════════════════

class AlgorithmWorker(QThread):
    finished = pyqtSignal(list)
    error    = pyqtSignal(str)

    def __init__(self, events_path: str, annual_path: str):
        super().__init__()
        self.events_path = events_path
        self.annual_path = annual_path

    def run(self):
        try:
            fw = TMKFramework(self.events_path, self.annual_path)
            fw.run()
            self.finished.emit(fw.results)
        except Exception as e:
            self.error.emit(str(e))


# ═══════════════════════════════════════════════════════════════════════════
# HELPER WIDGETS
# ═══════════════════════════════════════════════════════════════════════════

def _divider(vertical: bool = False) -> QFrame:
    f = QFrame()
    f.setFrameShape(
        QFrame.Shape.VLine if vertical else QFrame.Shape.HLine
    )
    f.setStyleSheet(f"color: {Colors.neutral_30}; background: {Colors.neutral_30};")
    if vertical:
        f.setFixedWidth(1)
    else:
        f.setFixedHeight(1)
    return f


def _scrollarea(widget: QWidget) -> QScrollArea:
    """Bungkus widget dalam QScrollArea yang sudah di-style."""
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setStyleSheet("background: transparent;" + SCROLLBAR_QSS)
    sa.setWidget(widget)
    return sa


class BadgeLabel(QLabel):
    """Badge pill berwarna — dipakai inline di tabel dan overview."""
    def __init__(self, text: str, fg: str, bg: str, parent=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {bg};
                color: {fg};
                border-radius: 4px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 500;
            }}
        """)
        self.setFixedHeight(20)

    @staticmethod
    def risk(tier: str) -> "BadgeLabel":
        return BadgeLabel(tier, RISK_FG.get(tier, "#333"), RISK_BG.get(tier, "#eee"))

    @staticmethod
    def contagion(tier: str) -> "BadgeLabel":
        return BadgeLabel(tier, CONTAGION_FG.get(tier, "#333"), CONTAGION_BG.get(tier, "#eee"))


class StatCard(QWidget):
    """Kartu metrik — label + angka besar."""
    def __init__(self, label: str, value: str = "—",
                 sub: str = "", value_color: str = None, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            StatCard {{
                background: {Colors.neutral_20};
                border-radius: 8px;
            }}
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(3)

        self._lbl = Typography(label, variant="c", color=Colors.neutral_60)
        lay.addWidget(self._lbl)

        self._val = Typography(value, variant="h6", weight="medium",
                               color=value_color or Colors.neutral_black)
        lay.addWidget(self._val)

        if sub:
            self._sub = Typography(sub, variant="c", color=Colors.neutral_50)
            lay.addWidget(self._sub)

    def update_value(self, v: str):
        self._val.setText(v)


# ═══════════════════════════════════════════════════════════════════════════
# FILTER BAR — pakai Typography + Button dari project
# ═══════════════════════════════════════════════════════════════════════════

_COMBO_QSS = f"""
    QComboBox {{
        border: 1px solid {Colors.neutral_30};
        border-radius: 6px;
        padding: 0 10px;
        font-size: 12px;
        color: {Colors.neutral_80};
        background: {Colors.neutral_white};
        font-family: "Plus Jakarta Sans";
    }}
    QComboBox:hover {{
        border-color: {Colors.neutral_50};
    }}
    QComboBox:focus {{
        border-color: {Colors.primary_main};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QComboBox::down-arrow {{
        width: 10px;
        height: 10px;
    }}
    QComboBox QAbstractItemView {{
        border: 1px solid {Colors.neutral_30};
        border-radius: 6px;
        background: {Colors.neutral_white};
        selection-background-color: {Colors.neutral_20};
        selection-color: {Colors.neutral_90};
        font-size: 12px;
        padding: 2px;
    }}
"""

_SEARCH_QSS = f"""
    QLineEdit {{
        border: 1px solid {Colors.neutral_30};
        border-radius: 6px;
        padding: 0 10px;
        font-size: 12px;
        color: {Colors.neutral_80};
        background: {Colors.neutral_white};
        font-family: "Plus Jakarta Sans";
    }}
    QLineEdit:hover {{
        border-color: {Colors.neutral_50};
    }}
    QLineEdit:focus {{
        border-color: {Colors.primary_main};
    }}
"""


def _combo(placeholder: str, items: list[str] = None,
           min_w: int = 140) -> QComboBox:
    cb = QComboBox()
    cb.addItem(placeholder)
    if items:
        cb.addItems(items)
    cb.setFixedHeight(34)
    cb.setMinimumWidth(min_w)
    cb.setStyleSheet(_COMBO_QSS)
    return cb


class FilterBar(QWidget):
    changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            FilterBar {{
                background: {Colors.neutral_white};
                border: 1px solid {Colors.neutral_30};
                border-radius: 8px;
            }}
        """)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(10)

        def _lbl(text):
            l = Typography(text, variant="c", color=Colors.neutral_60)
            l.setFixedHeight(34)
            l.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            return l

        self.cb_region  = _combo("Semua region")
        self.cb_country = _combo("Semua negara", min_w=150)
        self.cb_risk    = _combo("Semua risk",
                                 ["CRITICAL", "HIGH", "MEDIUM", "LOW"], min_w=130)
        self.cb_contag  = _combo("Semua contagion", ["HOT", "WARM", "COOL"], min_w=130)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cari negara / aktor / episode…")
        self.search.setFixedHeight(34)
        self.search.setStyleSheet(_SEARCH_QSS)

        self.btn_reset = Button("Reset", variant="outlined", size="sm")
        self.btn_reset.setFixedHeight(34)
        self.btn_reset.clicked.connect(self.reset)

        lay.addWidget(_lbl("Region:"))
        lay.addWidget(self.cb_region)
        lay.addWidget(_divider(vertical=True))
        lay.addWidget(_lbl("Negara:"))
        lay.addWidget(self.cb_country)
        lay.addWidget(_divider(vertical=True))
        lay.addWidget(_lbl("Risk:"))
        lay.addWidget(self.cb_risk)
        lay.addWidget(_divider(vertical=True))
        lay.addWidget(_lbl("Contagion:"))
        lay.addWidget(self.cb_contag)
        lay.addWidget(_divider(vertical=True))
        lay.addWidget(self.search, 1)
        lay.addWidget(self.btn_reset)

        for cb in [self.cb_region, self.cb_country, self.cb_risk, self.cb_contag]:
            cb.currentIndexChanged.connect(self.changed.emit)
        self.search.textChanged.connect(self.changed.emit)

    def populate(self, regions: list[str], countries: list[str]):
        self.cb_region.blockSignals(True)
        self.cb_country.blockSignals(True)
        for r in regions:
            self.cb_region.addItem(r)
        for c in countries:
            self.cb_country.addItem(c)
        self.cb_region.blockSignals(False)
        self.cb_country.blockSignals(False)

    def get_values(self) -> dict:
        def _v(cb, ph):
            t = cb.currentText()
            return None if t == ph else t
        return {
            "region":      _v(self.cb_region,  "Semua region"),
            "country":     _v(self.cb_country, "Semua negara"),
            "risk_type":   _v(self.cb_risk,    "Semua risk"),
            "contagion":   _v(self.cb_contag,  "Semua contagion"),
            "search_text": self.search.text().strip() or None,
        }

    def reset(self):
        self.cb_region.setCurrentIndex(0)
        self.cb_country.setCurrentIndex(0)
        self.cb_risk.setCurrentIndex(0)
        self.cb_contag.setCurrentIndex(0)
        self.search.clear()


# ═══════════════════════════════════════════════════════════════════════════
# BADGE TABLE — QTableWidget dengan support badge di cell tertentu
# ═══════════════════════════════════════════════════════════════════════════

# Kolom-kolom yang akan dirender sebagai badge (index 0-based dari TABLE_COLS)
_BADGE_COLS_RISK      = {8, 10}   # A* Risk, Combined
_BADGE_COLS_CONTAGION = {9}       # Contagion

TABLE_COLS = [
    "Negara", "Aktor", "Region", "Tahun", "Lvl",
    "Deaths", "A* Cost", "Pheromone",
    "A* Risk",    # 8 → badge risk
    "Contagion",  # 9 → badge contagion
    "Combined",   # 10 → badge risk
    "GP",
]

_TABLE_QSS = f"""
    QTableWidget {{
        border: 1px solid {Colors.neutral_30};
        border-radius: 8px;
        background: {Colors.neutral_white};
        gridline-color: {Colors.neutral_20};
        font-size: 12px;
        font-family: "Plus Jakarta Sans";
        outline: 0;
    }}
    QTableWidget::item {{
        padding: 4px 10px;
        color: {Colors.neutral_80};
        border: none;
    }}
    QTableWidget::item:selected {{
        background: {Colors.neutral_20};
        color: {Colors.neutral_90};
    }}
    QHeaderView::section {{
        background: {Colors.neutral_20};
        color: {Colors.neutral_60};
        font-size: 11px;
        font-weight: 500;
        font-family: "Plus Jakarta Sans";
        padding: 6px 10px;
        border: none;
        border-bottom: 1px solid {Colors.neutral_30};
        border-right: 1px solid {Colors.neutral_30};
    }}
    QHeaderView::section:last {{
        border-right: none;
    }}
    QTableCornerButton::section {{
        background: {Colors.neutral_20};
        border: none;
    }}
""" + SCROLLBAR_QSS


class BadgeTable(QWidget):
    """
    Table yang support badge di kolom tertentu + pagination.
    Menggantikan PaginationTable untuk halaman Tabel Episode.
    """

    _COL_WIDTHS = {
        0: 120, 1: 140, 2: 110, 3: 56, 4: 36,
        5: 80, 6: 72, 7: 78,
        8: 94, 9: 94, 10: 94, 11: 36,
    }

    def __init__(self, page_size: int = 15, parent=None):
        super().__init__(parent)
        self._all_rows: list[list] = []
        self._page      = 1
        self._page_size = page_size

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Table widget
        self._tbl = QTableWidget()
        self._tbl.setColumnCount(len(TABLE_COLS))
        self._tbl.setHorizontalHeaderLabels(TABLE_COLS)
        self._tbl.verticalHeader().setVisible(False)
        self._tbl.setShowGrid(True)
        self._tbl.setAlternatingRowColors(False)
        self._tbl.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._tbl.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tbl.setSortingEnabled(False)
        self._tbl.setStyleSheet(_TABLE_QSS)
        self._tbl.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._tbl.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        hdr = self._tbl.horizontalHeader()
        for col, w in self._COL_WIDTHS.items():
            self._tbl.setColumnWidth(col, w)
        hdr.setStretchLastSection(False)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self._tbl.verticalHeader().setDefaultSectionSize(36)
        lay.addWidget(self._tbl, 1)

        # Pagination bar
        pbar = QWidget()
        pbar.setStyleSheet("background: transparent;")
        pbar_lay = QHBoxLayout(pbar)
        pbar_lay.setContentsMargins(0, 0, 0, 0)
        pbar_lay.setSpacing(8)

        self._info    = Typography("", variant="c", color=Colors.neutral_60)
        self._btn_prv = Button("← Prev", variant="outlined", size="sm")
        self._btn_prv.setFixedHeight(32)
        self._page_lbl = Typography("", variant="c", color=Colors.neutral_70)
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._btn_nxt = Button("Next →", variant="outlined", size="sm")
        self._btn_nxt.setFixedHeight(32)

        self._btn_prv.clicked.connect(self._prev)
        self._btn_nxt.clicked.connect(self._next)

        pbar_lay.addWidget(self._info)
        pbar_lay.addStretch()
        pbar_lay.addWidget(self._btn_prv)
        pbar_lay.addWidget(self._page_lbl)
        pbar_lay.addWidget(self._btn_nxt)
        lay.addWidget(pbar)

    def set_rows(self, rows: list[list]):
        self._all_rows = rows
        self._page = 1
        self._render()

    def _total_pages(self) -> int:
        return max(1, -(-len(self._all_rows) // self._page_size))

    def _render(self):
        start  = (self._page - 1) * self._page_size
        end    = start + self._page_size
        chunk  = self._all_rows[start:end]
        n      = len(self._all_rows)
        total  = self._total_pages()

        self._tbl.setRowCount(len(chunk))

        for row_idx, row in enumerate(chunk):
            self._tbl.setRowHeight(row_idx, 36)
            for col_idx, val in enumerate(row):
                text = str(val)

                if col_idx in _BADGE_COLS_RISK:
                    # Render badge sebagai widget
                    b = BadgeLabel.risk(text)
                    cell_w = QWidget()
                    cell_w.setStyleSheet("background: transparent;")
                    cell_lay = QHBoxLayout(cell_w)
                    cell_lay.setContentsMargins(6, 0, 6, 0)
                    cell_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cell_lay.addWidget(b)
                    self._tbl.setCellWidget(row_idx, col_idx, cell_w)

                elif col_idx in _BADGE_COLS_CONTAGION:
                    b = BadgeLabel.contagion(text)
                    cell_w = QWidget()
                    cell_w.setStyleSheet("background: transparent;")
                    cell_lay = QHBoxLayout(cell_w)
                    cell_lay.setContentsMargins(6, 0, 6, 0)
                    cell_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    cell_lay.addWidget(b)
                    self._tbl.setCellWidget(row_idx, col_idx, cell_w)

                else:
                    item = QTableWidgetItem(text)
                    item.setTextAlignment(
                        Qt.AlignmentFlag.AlignVCenter
                        | (Qt.AlignmentFlag.AlignRight
                           if col_idx in {3, 4, 5, 6, 7} else
                           Qt.AlignmentFlag.AlignLeft)
                    )
                    self._tbl.setItem(row_idx, col_idx, item)

        self._info.setText(
            f"Menampilkan {start+1}–{min(end,n)} dari {n} episode"
        )
        self._page_lbl.setText(f"Halaman {self._page} / {total}")
        self._btn_prv.setDisabled(self._page <= 1)
        self._btn_nxt.setDisabled(self._page >= total)

    def _prev(self):
        if self._page > 1:
            self._page -= 1
            self._render()

    def _next(self):
        if self._page < self._total_pages():
            self._page += 1
            self._render()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 0 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════

class OverviewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        inner = QWidget()
        inner.setStyleSheet(f"background: {Colors.neutral_10};")
        self._root = QVBoxLayout(inner)
        self._root.setContentsMargins(24, 20, 24, 24)
        self._root.setSpacing(20)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(_scrollarea(inner))

        self._stat_cards: dict[str, StatCard] = {}
        self._build_stat_row()
        self._build_section("Distribusi combined risk")

        self.chart_risk = BarChart(
            title="", x_label="Risk tier", y_label="Jumlah episode",
            figsize=(8, 3.2)
        )
        self._root.addWidget(self.chart_risk)

        self._build_section("Risiko per region")
        self.region_grid = QGridLayout()
        self.region_grid.setSpacing(10)
        self._root.addLayout(self.region_grid)

        self._build_section("Top 10 episode CRITICAL")
        self.top10_lay = QVBoxLayout()
        self.top10_lay.setSpacing(5)
        self._root.addLayout(self.top10_lay)

        self._build_section("Top 10 negara — pheromone ACO tertinggi")
        self.phero_lay = QVBoxLayout()
        self.phero_lay.setSpacing(5)
        self._root.addLayout(self.phero_lay)

        self._build_section("Validasi ground truth (genpol_onset)")
        self.val_label = Typography("—", variant="p", color=Colors.neutral_70,
                                    word_wrap=True)
        self._root.addWidget(self.val_label)
        self._root.addStretch()

    def _build_stat_row(self):
        row = QHBoxLayout()
        row.setSpacing(12)
        defs = [
            ("n_episodes", "Total episode",     "—", None),
            ("n_critical", "CRITICAL",          "—", RISK_FG["CRITICAL"]),
            ("avg_cost",   "Avg A* cost",        "—", None),
            ("accuracy",   "Akurasi validasi",   "—", RISK_FG["LOW"]),
        ]
        for key, label, val, color in defs:
            card = StatCard(label, val, value_color=color)
            self._stat_cards[key] = card
            row.addWidget(card)
        self._root.addLayout(row)

    def _build_section(self, title: str):
        lbl = Typography(title, variant="t", weight="medium",
                         color=Colors.neutral_80)
        self._root.addSpacing(4)
        self._root.addWidget(lbl)
        self._root.addWidget(_divider())

    def load(self, stats: dict):
        dist = stats["distribution"]
        n    = stats["n_episodes"]

        self._stat_cards["n_episodes"].update_value(str(n))
        crit = dist.get("CRITICAL", 0)
        self._stat_cards["n_critical"].update_value(
            f"{crit}  ({crit/n*100:.0f}%)"
        )
        self._stat_cards["avg_cost"].update_value(str(stats["avg_astar_cost"]))
        self._stat_cards["accuracy"].update_value(f"{stats['accuracy']}%")

        self.chart_risk.plot_risk_distribution(dist)

        # Region cards
        while self.region_grid.count():
            item = self.region_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i, (region, counts) in enumerate(
            sorted(stats["region_breakdown"].items(),
                   key=lambda x: -x[1].get("CRITICAL", 0))
        ):
            r, c = divmod(i, 3)
            self.region_grid.addWidget(
                self._region_card(region, counts), r, c
            )

        # Top 10 critical
        self._clear_layout(self.top10_lay)
        for ep in stats["top10_critical"]:
            self.top10_lay.addWidget(self._ep_row(ep))

        # Top 10 pheromone
        self._clear_layout(self.phero_lay)
        for country, tau in stats["top10_pheromone"]:
            self.phero_lay.addWidget(self._phero_row(country, tau))

        gp  = stats["genpol_total"]
        hit = stats["genpol_hit"]
        self.val_label.setText(
            f"Episode aktual genosida (genpol_onset=1): {gp}   |   "
            f"Diprediksi CRITICAL/HIGH: {hit}   |   "
            f"Akurasi recall: {stats['accuracy']}%"
        )

    @staticmethod
    def _clear_layout(lay: QVBoxLayout):
        while lay.count():
            item = lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _region_card(self, region: str, counts: dict) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            QWidget {{
                background: {Colors.neutral_white};
                border: 1px solid {Colors.neutral_30};
                border-radius: 8px;
            }}
        """)
        l = QVBoxLayout(w)
        l.setContentsMargins(14, 10, 14, 10)
        l.setSpacing(6)
        l.addWidget(Typography(region, variant="b", weight="medium",
                                color=Colors.neutral_80))
        badges = QHBoxLayout()
        badges.setSpacing(5)
        for tier in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            cnt = counts.get(tier, 0)
            if cnt:
                badges.addWidget(
                    BadgeLabel(
                        f"{cnt} {tier[:4].lower()}",
                        RISK_FG[tier], RISK_BG[tier]
                    )
                )
        badges.addStretch()
        l.addLayout(badges)
        return w

    def _ep_row(self, ep: EpisodeResult) -> QWidget:
        w = QWidget()
        w.setStyleSheet(f"""
            QWidget {{
                background: {Colors.neutral_white};
                border: 1px solid {Colors.neutral_30};
                border-radius: 6px;
            }}
        """)
        l = QHBoxLayout(w)
        l.setContentsMargins(14, 8, 14, 8)
        l.setSpacing(14)

        country_lbl = Typography(
            f"{ep.country}  {ep.onset_year}", variant="b",
            weight="medium", color=Colors.neutral_80
        )
        country_lbl.setFixedWidth(170)

        l.addWidget(country_lbl)
        l.addWidget(Typography(f"L{ep.ordinal}", variant="c",
                                color=Colors.neutral_60))
        l.addWidget(Typography(f"{ep.total_deaths:,} deaths", variant="c",
                                color=Colors.neutral_60))
        l.addWidget(Typography(ep.region, variant="c",
                                color=Colors.neutral_50), 1)
        l.addWidget(BadgeLabel.risk("CRITICAL"))
        return w

    def _phero_row(self, country: str, tau: float) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 2, 0, 2)
        l.setSpacing(12)

        name = Typography(country, variant="b", color=Colors.neutral_70)
        name.setFixedWidth(180)

        bar_out = QWidget()
        bar_out.setFixedHeight(8)
        bar_out.setStyleSheet(
            f"background:{Colors.neutral_30}; border-radius:4px;"
        )
        bar_out.setMinimumWidth(200)
        bar_in = QWidget(bar_out)
        bar_in.setFixedHeight(8)
        bar_in.setFixedWidth(max(4, int(tau * 200)))
        c = (RISK_FG["CRITICAL"] if tau > 0.7
             else RISK_FG["HIGH"] if tau >= 0.3
             else RISK_FG["LOW"])
        bar_in.setStyleSheet(f"background:{c}; border-radius:4px;")

        val = Typography(f"{tau:.3f}", variant="c", color=Colors.neutral_60)
        val.setFixedWidth(42)
        val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        val.setStyleSheet(
            f"font-family: monospace; color:{Colors.neutral_60}; background:transparent;"
        )

        l.addWidget(name)
        l.addWidget(bar_out, 1)
        l.addWidget(val)
        return w


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 1 — TABEL EPISODE
# ═══════════════════════════════════════════════════════════════════════════

class TablePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background: {Colors.neutral_10};")
        self._all_results: list[EpisodeResult] = []

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 16)
        lay.setSpacing(10)

        self.filter_bar = FilterBar()
        self.filter_bar.changed.connect(self._apply_filter)
        lay.addWidget(self.filter_bar)

        self.row_count = Typography("—", variant="c", color=Colors.neutral_50)
        lay.addWidget(self.row_count)

        self.table = BadgeTable(page_size=15)
        lay.addWidget(self.table, 1)

    def load(self, results: list[EpisodeResult],
             regions: list[str], countries: list[str]):
        self._all_results = results
        self.filter_bar.populate(regions, countries)
        self._apply_filter()

    def _apply_filter(self):
        f = self.filter_bar.get_values()
        filtered = [
            r for r in self._all_results
            if (not f["region"]     or r.region        == f["region"])
            and (not f["country"]   or r.country       == f["country"])
            and (not f["risk_type"] or r.combined_risk  == f["risk_type"])
            and (not f["contagion"] or r.contagion_tier == f["contagion"])
            and (not f["search_text"]
                 or f["search_text"].lower() in r.country.lower()
                 or f["search_text"].lower() in r.actor.lower()
                 or f["search_text"].lower() in r.tmk_id.lower())
        ]
        self.row_count.setText(
            f"Menampilkan {len(filtered)} dari {len(self._all_results)} episode"
        )
        rows = []
        for r in filtered:
            rows.append([
                r.country,
                r.actor[:30] + ("…" if len(r.actor) > 30 else ""),
                r.region,
                str(r.onset_year),
                str(r.ordinal),
                f"{r.total_deaths:,}",
                f"{r.astar_cost:.3f}",
                f"{r.pheromone:.3f}",
                r.risk_search,       # col 8 → badge risk
                r.contagion_tier,    # col 9 → badge contagion
                r.combined_risk,     # col 10 → badge risk
                "✓" if r.genpol_onset else "—",
            ])
        self.table.set_rows(rows)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE 2 — GRAFIK
# ═══════════════════════════════════════════════════════════════════════════

class ChartsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_results: list[EpisodeResult] = []

        inner = QWidget()
        inner.setStyleSheet(f"background: {Colors.neutral_10};")
        self._root = QVBoxLayout(inner)
        self._root.setContentsMargins(24, 20, 24, 24)
        self._root.setSpacing(20)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(_scrollarea(inner))

        # Region filter
        top = QHBoxLayout()
        top.setSpacing(10)
        top.addWidget(Typography("Filter region:", variant="b",
                                  color=Colors.neutral_60))
        self.cb_region = _combo("Semua region", min_w=170)
        self.cb_region.currentIndexChanged.connect(self._redraw)
        top.addWidget(self.cb_region)
        top.addStretch()
        self._root.addLayout(top)

        # ── chart 1: risk distribution ───────────────────────────────────
        self._section("Distribusi combined risk")
        self.chart_risk = BarChart(
            title="", x_label="Risk tier", y_label="Jumlah episode",
            figsize=(8, 3.2)
        )
        self._root.addWidget(self.chart_risk)

        # ── chart 2: top 15 A* cost ──────────────────────────────────────
        self._section("Top 15 — A* cost tertinggi (eskalasi paling susah)")
        self.chart_astar = BarChart(
            title="", x_label="A* cost", y_label="",
            horizontal=True, figsize=(8, 6)        # lebih tinggi
        )
        self._root.addWidget(self.chart_astar)

        # ── chart 3: top 15 pheromone ────────────────────────────────────
        self._section("Top 15 — pheromone ACO tertinggi (contagion hotspot)")
        self.chart_phero = BarChart(
            title="", x_label="Pheromone", y_label="",
            horizontal=True, figsize=(8, 6)        # lebih tinggi
        )
        self._root.addWidget(self.chart_phero)

        # ── chart 4: scatter ─────────────────────────────────────────────
        self._section("Scatter — A* cost vs pheromone  (tiap titik = 1 episode)")
        self.chart_scatter = ScatterPlot(
            title="",
            x_label="A* cost  (rendah = mudah eskalasi)",
            y_label="Pheromone ACO",
            figsize=(8, 4.5),                      # lebih tinggi
        )
        self.chart_scatter.setFixedHeight(700)
        self.chart_astar.setFixedHeight(500)
        self.chart_risk.setFixedHeight(600)
        self.chart_phero.setFixedHeight(600)
        self._root.addWidget(self.chart_scatter)

        self._root.addStretch()

    def _section(self, title: str):
        self._root.addWidget(
            Typography(title, variant="t", weight="medium",
                       color=Colors.neutral_80)
        )
        self._root.addWidget(_divider())

    def load(self, results: list[EpisodeResult], regions: list[str]):
        self._all_results = results
        for r in regions:
            self.cb_region.addItem(r)
        self._redraw()

    def _redraw(self):
        if not self._all_results:
            return
        sel  = self.cb_region.currentText()
        data = (
            [r for r in self._all_results if r.region == sel]
            if sel != "Semua region"
            else self._all_results
        )
        if not data:
            return

        # chart 1 — risk dist
        dist = {t: 0 for t in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]}
        for r in data:
            dist[r.combined_risk] += 1
        self.chart_risk.plot_risk_distribution(dist)

        # chart 2 — top 15 A* cost
        top15c = sorted(data, key=lambda r: -r.astar_cost)[:15]
        self.chart_astar.plot(
            labels=[f"{r.country} {r.onset_year}" for r in top15c],
            values=[r.astar_cost for r in top15c],
            colors=[RISK_FG[r.combined_risk] for r in top15c],
            value_fmt="{:.2f}",
        )

        # chart 3 — top 15 pheromone
        cphi: dict[str, float] = {}
        for r in data:
            if r.country not in cphi or r.pheromone > cphi[r.country]:
                cphi[r.country] = r.pheromone
        top15p = sorted(cphi.items(), key=lambda x: -x[1])[:15]
        self.chart_phero.plot(
            labels=[c for c, _ in top15p],
            values=[v for _, v in top15p],
            colors=[
                RISK_FG["CRITICAL"] if v > 0.7
                else RISK_FG["HIGH"] if v >= 0.3
                else RISK_FG["LOW"]
                for _, v in top15p
            ],
            value_fmt="{:.3f}",
        )

        # chart 4 — scatter
        tier_idx = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        self.chart_scatter.plot(
            points=[[r.astar_cost, r.pheromone] for r in data],
            labels=[tier_idx[r.combined_risk] for r in data],
            annotations=None,
            n_clusters=4,
        )


# ═══════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════════════════

class SidebarButton(QPushButton):
    def __init__(self, text: str, index: int, parent=None):
        super().__init__(text, parent)
        self.index = index
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(38)
        self.set_active(False)

    def set_active(self, active: bool):
        if active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Colors.primary_main};
                    color: {Colors.neutral_white};
                    border: none; border-radius: 6px;
                    text-align: left; padding: 0 14px;
                    font-size: 13px; font-weight: 500;
                    font-family: "Plus Jakarta Sans";
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {Colors.neutral_60};
                    border: none; border-radius: 6px;
                    text-align: left; padding: 0 14px;
                    font-size: 13px;
                    font-family: "Plus Jakarta Sans";
                }}
                QPushButton:hover {{
                    background: {Colors.neutral_20};
                    color: {Colors.neutral_80};
                }}
            """)


# ═══════════════════════════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    def __init__(self, events_path: str, annual_path: str):
        super().__init__()
        self.events_path = events_path
        self.annual_path = annual_path
        self.setWindowTitle("TMK Genocide Risk Framework — A* + ACO")
        self.setMinimumSize(WIN_W, WIN_H)
        self.resize(WIN_W, WIN_H)
        self._build_ui()
        self._start_computation()

    # ── build ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setStyleSheet(f"background: {Colors.neutral_10};")
        self.setCentralWidget(root)

        lay = QHBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        lay.addWidget(self._build_sidebar())
        lay.addWidget(_divider(vertical=True))

        content = QWidget()
        content.setStyleSheet(f"background: {Colors.neutral_10};")
        cv = QVBoxLayout(content)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)
        cv.addWidget(self._build_topbar())
        cv.addWidget(_divider())

        self.stack          = QStackedWidget()
        self.overview_page  = OverviewPage()
        self.table_page     = TablePage()
        self.charts_page    = ChartsPage()
        self.stack.addWidget(self.overview_page)
        self.stack.addWidget(self.table_page)
        self.stack.addWidget(self.charts_page)
        cv.addWidget(self.stack, 1)

        lay.addWidget(content, 1)

    def _build_sidebar(self) -> QWidget:
        sb = QWidget()
        sb.setFixedWidth(SIDEBAR_W)
        sb.setStyleSheet(f"background: {Colors.neutral_white};")

        lay = QVBoxLayout(sb)
        lay.setContentsMargins(14, 22, 14, 18)
        lay.setSpacing(6)

        logo = QLabel("TMK Risk")
        logo.setStyleSheet(
            f"font-size:15px; font-weight:700; color:{Colors.neutral_90};"
            f" background:transparent; font-family:'Plus Jakarta Sans';"
        )
        lay.addWidget(logo)

        sub = Typography("A* + ACO Framework", variant="c",
                         color=Colors.neutral_50)
        lay.addWidget(sub)
        lay.addSpacing(14)
        lay.addWidget(_divider())
        lay.addSpacing(10)

        nav_lbl = QLabel("NAVIGASI")
        nav_lbl.setStyleSheet(
            f"font-size:9px; font-weight:600; color:{Colors.neutral_40};"
            f" letter-spacing:1.2px; background:transparent;"
            f" padding: 0 14px; font-family:'Plus Jakarta Sans';"
        )
        lay.addWidget(nav_lbl)
        lay.addSpacing(4)

        self._nav_btns: list[SidebarButton] = []
        for i, name in enumerate(NAV_ITEMS):
            btn = SidebarButton(name, i)
            btn.clicked.connect(lambda _, idx=i: self._go(idx))
            self._nav_btns.append(btn)
            lay.addWidget(btn)

        self._nav_btns[0].set_active(True)
        lay.addStretch()

        self.status_lbl = Typography(
            "Memuat data…", variant="c", color=Colors.neutral_50,
            word_wrap=True
        )
        lay.addWidget(self.status_lbl)
        return sb

    def _build_topbar(self) -> QWidget:
        tb = QWidget()
        tb.setFixedHeight(52)
        tb.setStyleSheet(f"background: {Colors.neutral_white};")

        lay = QHBoxLayout(tb)
        lay.setContentsMargins(24, 12, 24, 0)
        lay.setSpacing(12)

        self.page_title = Typography(
            "Overview", variant="h6", weight="medium",
            color=Colors.neutral_90
        )
        lay.addWidget(self.page_title)
        lay.addStretch()

        self.meta_lbl = Typography(
            "214 episode | 63 negara | 1946–2022",
            variant="c", color=Colors.neutral_50
        )
        lay.addWidget(self.meta_lbl)
        return tb

    # ── navigation ────────────────────────────────────────────────────────

    def _go(self, idx: int):
        self.stack.setCurrentIndex(idx)
        for i, btn in enumerate(self._nav_btns):
            btn.set_active(i == idx)
        self.page_title.setText(NAV_ITEMS[idx])

    # ── computation ───────────────────────────────────────────────────────

    def _start_computation(self):
        self.status_lbl.setText("Menjalankan A* + ACO…")
        self._worker = AlgorithmWorker(self.events_path, self.annual_path)
        self._worker.finished.connect(self._on_done)
        self._worker.error.connect(self._on_err)
        self._worker.start()

    def _on_done(self, results: list[EpisodeResult]):
        self._results = results
        fw = TMKFramework.__new__(TMKFramework)
        fw.results = results
        fw._ran = True
        stats    = fw.get_stats()
        regions  = sorted(set(r.region  for r in results))
        countries = sorted(set(r.country for r in results))

        self.overview_page.load(stats)
        self.table_page.load(results, regions, countries)
        self.charts_page.load(results, regions)

        n    = len(results)
        crit = stats["distribution"].get("CRITICAL", 0)
        self.status_lbl.setText(
            f"{n} episode\n{crit} CRITICAL\nAkurasi: {stats['accuracy']}%"
        )
        self.status_lbl.setStyleSheet(
            f"font-size:10px; color:{Colors.success_main};"
            f" background:transparent; font-family:'Plus Jakarta Sans';"
        )

    def _on_err(self, msg: str):
        self.status_lbl.setText(f"Error:\n{msg}")
        self.status_lbl.setStyleSheet(
            f"font-size:10px; color:{Colors.error_main};"
            f" background:transparent;"
        )


# ═══════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="TMK Risk Framework — GUI Dashboard"
    )
    parser.add_argument(
        "--events",
        default=resource_path("contents/tmk_events_release_1.2.xls"),
    )
    parser.add_argument(
        "--annual",
        default=resource_path("contents/tmk_annual_release_1.2.xlsx"),
    )
    args = parser.parse_args()

    for fpath, label in [(args.events, "events"), (args.annual, "annual")]:
        if not Path(fpath).exists():
            print(f"[ERROR] File {label} tidak ditemukan: {fpath}")
            sys.exit(1)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    try:
        Fonts().load_fonts()
    except Exception:
        pass

    win = MainWindow(args.events, args.annual)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()