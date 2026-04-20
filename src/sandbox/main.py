"""
sandbox/showcase.py

Testing semua components sekaligus.
Jalankan: python -m src.sandbox.showcase
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from PyQt6.QtWidgets import QApplication, QWidget, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from src.components import (
    Colors, Typography, Button,
    VBox, HBox,
    UploadFile, Table, PaginationTable,
    ScatterPlot, LineChart,
)


class Showcase(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Component Showcase")
        self.setMinimumSize(900, 700)
        self.setStyleSheet(f"background-color: {Colors.neutral_20};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")

        container = QWidget()
        container.setStyleSheet(f"background-color: {Colors.neutral_20};")
        root = VBox(spacing=32, margin=(32, 32, 32, 32))
        container.setLayout(root)

        scroll.setWidget(container)

        outer = VBox(spacing=0)
        outer.addWidget(scroll)
        self.setLayout(outer)

        self._section_typography(root)
        self._section_buttons(root)
        self._section_upload(root)
        self._section_table(root)
        self._section_scatter(root)
        self._section_line(root)

    # ── helpers ──────────────────────────────────────────────────
    def _divider(self, layout, label: str):
        layout.addWidget(Typography(label, variant="h6", weight="bold", color=Colors.neutral_80))
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"color: {Colors.neutral_30};")
        layout.addWidget(line)

    # ── sections ─────────────────────────────────────────────────
    def _section_typography(self, root):
        self._divider(root, "Typography")

        for variant in ["h1", "h2", "h3", "h4", "h5", "h6", "t", "p", "b", "c"]:
            root.addWidget(Typography(f"variant={variant}  |  The quick brown fox", variant=variant))

    def _section_buttons(self, root):
        self._divider(root, "Button Variants")

        row1 = HBox(spacing=12)
        for v in ["primary", "success", "warning", "error"]:
            row1.addWidget(Button(v.capitalize(), variant=v))
        root.addLayout(row1)

        row2 = HBox(spacing=12)
        for v in ["alternative", "outlined"]:
            row2.addWidget(Button(v.capitalize(), variant=v))
        row2.addWidget(Button("Disabled", variant="primary").also(lambda b: b.setDisabled(True)))
        root.addLayout(row2)

        row3 = HBox(spacing=12)
        for s in ["sm", "md", "lg"]:
            row3.addWidget(Button(f"size={s}", size=s))
        root.addLayout(row3)

    def _section_upload(self, root):
        self._divider(root, "Upload File")

        upload = UploadFile(accept="CSV Files (*.csv)")
        upload.file_selected.connect(lambda path: print(f"[Upload] selected: {path}"))
        root.addWidget(upload)

    def _section_table(self, root):
        self._divider(root, "Pagination Table")

        dummy_rows = [
            [f"Country {i}", i * 10, i * 5, i % 3]
            for i in range(1, 36)
        ]

        tbl = PaginationTable(
            columns=["Country", "Value A", "Value B", "Cluster"],
            rows=dummy_rows,
            page_size=8,
        )
        root.addWidget(tbl)

    def _section_scatter(self, root):
        self._divider(root, "Scatter Plot")

        import random
        random.seed(0)

        points = [[random.uniform(0, 1), random.uniform(0, 1)] for _ in range(30)]
        labels = [random.randint(0, 2) for _ in range(30)]
        names  = [f"Country {i}" for i in range(30)]

        chart = ScatterPlot(title="FCM Clustering Result", x_label="Dim 1", y_label="Dim 2")
        chart.plot(points=points, labels=labels, annotations=names, n_clusters=3)
        root.addWidget(chart)

    def _section_line(self, root):
        self._divider(root, "Line Chart — Elbow Method")

        chart = LineChart(title="Elbow Method", x_label="Cluster (C)", y_label="Objective Function (J)")
        chart.plot(series=[{
            "label": "J value",
            "x": list(range(2, 9)),
            "y": [0.85, 0.61, 0.45, 0.38, 0.33, 0.30, 0.28],
        }])
        root.addWidget(chart)


# monkey-patch .also() untuk one-liner disabled
def _also(widget, fn):
    fn(widget)
    return widget

import PyQt6.QtWidgets as _qw
_qw.QWidget.also = _also


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = Showcase()
    win.show()
    sys.exit(app.exec())