from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from typing import Optional
from .colors import Colors


class Table(QTableWidget):
    def __init__(
        self,
        columns: list[str],
        rows: list[list] = [],
        stretch_last: bool = True,
        col_widths: Optional[dict[str | int, int]] = None,   # bisa nama atau index
        col_aligns: Optional[dict[str | int, Qt.AlignmentFlag]] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.columns     = columns
        self._col_widths = self._resolve(col_widths or {}, columns)
        self._col_aligns = self._resolve(col_aligns or {}, columns)

        self.columns = columns
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)

        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)

        header = self.horizontalHeader()
        header.setStretchLastSection(False)  
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Apply col_widths
        for col_idx, width in self._col_widths.items():
            header.setSectionResizeMode(col_idx, QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(col_idx, width)

        # Stretch kolom terakhir kalau tidak di-set manual
        if stretch_last:
            last = len(columns) - 1
            if last not in self._col_widths:
                header.setSectionResizeMode(last, QHeaderView.ResizeMode.Stretch)

        self._apply_style()

        if rows:
            self.set_rows(rows)

    def _apply_style(self):
        self.setStyleSheet(f"""
            QTableWidget {{
                background-color:    {Colors.neutral_white};
                alternate-background-color: {Colors.neutral_10};
                border:              1px solid {Colors.neutral_30};
                border-radius:       8px;
                outline:             none;
                font-family:         Inter;
                font-size:           13px;
                color:               {Colors.neutral_black};
                gridline-color:      transparent;
            }}
            QTableWidget::item {{
                padding:  8px 12px;
                border:   none;
            }}
            QTableWidget::item:selected {{
                background-color: #DBEAFE;
                color:            {Colors.neutral_black};
            }}
            QHeaderView::section {{
                background-color: {Colors.neutral_20};
                color:            {Colors.neutral_70};
                font-weight:      600;
                font-size:        12px;
                font-family:      Inter;
                padding:          8px 12px;
                border:           none;
                border-bottom:    1px solid {Colors.neutral_30};
            }}
            QScrollBar:vertical {{
                width: 6px;
                background: transparent;
            }}
            QScrollBar::handle:vertical {{
                background:    {Colors.neutral_40};
                border-radius: 3px;
            }}
        """)

    def set_rows(self, rows: list[list]):
        self.setRowCount(len(rows))

        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))

                # pakai col_aligns kalau ada, fallback ke AlignLeft
                align = self._col_aligns.get(
                    col_idx,
                    Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                )
                item.setTextAlignment(align)
                self.setItem(row_idx, col_idx, item)

        self.resizeRowsToContents()

    def clear_rows(self):
        self.setRowCount(0)

    def append_row(self, row_data: list):
        row_idx = self.rowCount()
        self.insertRow(row_idx)

        for col_idx, value in enumerate(row_data):
            item = QTableWidgetItem(str(value))
            align = self._col_aligns.get(
                col_idx,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            item.setTextAlignment(align)
            self.setItem(row_idx, col_idx, item)

    @staticmethod
    def _resolve(d: dict, columns: list[str]) -> dict[int, any]:
        """Konversi key nama kolom → index, biarkan key int tetap."""
        result = {}
        for k, v in d.items():
            if isinstance(k, str):
                if k in columns:
                    result[columns.index(k)] = v
            else:
                result[k] = v
        return result