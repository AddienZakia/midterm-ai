from PyQt6.QtWidgets import QWidget, QSizePolicy
from PyQt6.QtCore import Qt
from typing import Optional
from .table import Table
from .button import Button
from .typography import Typography
from .layout import VBox, HBox
from .colors import Colors


class PaginationTable(QWidget):
    def __init__(
        self,
        columns: list[str],
        rows: list[list] = [],
        page_size: int = 10,
        col_widths: Optional[dict[int, int]] = None,
        col_aligns: Optional[dict[int, Qt.AlignmentFlag]] = None,
        parent=None,
    ):
        super().__init__(parent)

        

        self._all_rows  = rows
        self._page_size = page_size
        self._current   = 1

        layout = VBox(spacing=12)
        self.setLayout(layout)

        # ── table ─────────────────────────────────────────────────
        self.table = Table(
            columns=columns,
            col_widths=col_widths,
            col_aligns=col_aligns,
        )
        layout.addWidget(self.table)

        # ── pagination bar ────────────────────────────────────────
        bar = QWidget()
        bar_layout = HBox(spacing=8, align=Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight)
        bar.setLayout(bar_layout)

        self.info_label = Typography("", variant="c", color=Colors.neutral_60)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        bar_layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignVCenter)
        bar_layout.addStretch()

        self.btn_prev = Button("← Prev", variant="outlined", size="sm")
        self.btn_prev.clicked.connect(self._prev_page)
        bar_layout.addWidget(self.btn_prev, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.page_label = Typography("", variant="c", color=Colors.neutral_70)
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter)
        bar_layout.addWidget(self.page_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        self.btn_next = Button("Next →", variant="outlined", size="sm")
        self.btn_next.clicked.connect(self._next_page)
        bar_layout.addWidget(self.btn_next, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(bar)

        self.set_rows(rows)

    # ── public ───────────────────────────────────────────────────
    def set_rows(self, rows: list[list]):
        self._all_rows = rows
        self._current  = 1
        self._render()

    def set_page_size(self, size: int):
        self._page_size = size
        self._current   = 1
        self._render()

    # ── private ──────────────────────────────────────────────────
    def _total_pages(self) -> int:
        if not self._all_rows:
            return 1
        return max(1, -(-len(self._all_rows) // self._page_size))  # ceil div

    def _render(self):
        total  = self._total_pages()
        start  = (self._current - 1) * self._page_size
        end    = start + self._page_size
        slice_ = self._all_rows[start:end]

        self.table.set_rows(slice_)

        n = len(self._all_rows)
        self.info_label.setText(
            f"Showing {start + 1}–{min(end, n)} of {n} rows"
        )
        self.page_label.setText(f"Page {self._current} / {total}")

        self.btn_prev.setDisabled(self._current <= 1)
        self.btn_next.setDisabled(self._current >= total)

    def _prev_page(self):
        if self._current > 1:
            self._current -= 1
            self._render()

    def _next_page(self):
        if self._current < self._total_pages():
            self._current += 1
            self._render()