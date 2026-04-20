"""
bar_chart.py
============
Komponen BarChart menggunakan matplotlib + PyQt6.
Mendukung horizontal dan vertical bar, dengan styling
yang konsisten dengan komponen chart lainnya.
"""

from PyQt6.QtWidgets import QWidget, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import Optional
from .layout import VBox


BAR_COLORS = [
    "#2563EB",
    "#DC2626",
    "#16A34A",
    "#D97706",
    "#7C3AED",
    "#DB2777",
    "#0891B2",
    "#EA580C",
]

RISK_COLORS = {
    "CRITICAL": "#DC2626",
    "HIGH":     "#D97706",
    "MEDIUM":   "#2563EB",
    "LOW":      "#16A34A",
}


class BarChart(QWidget):
    def __init__(
        self,
        title:      str = "Bar Chart",
        x_label:    str = "X",
        y_label:    str = "Y",
        horizontal: bool = False,
        figsize:    tuple[float, float] = (7, 4),
        parent=None,
    ):
        super().__init__(parent)

        self._title      = title
        self._x_label    = x_label
        self._y_label    = y_label
        self._horizontal = horizontal

        layout = VBox(spacing=0)
        self.setLayout(layout)

        self.figure = Figure(figsize=figsize, dpi=100, facecolor="#F8FAFC")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        layout.addWidget(self.canvas)
        self._draw_empty()

    def _draw_empty(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self._style_axes(ax)
        self.figure.tight_layout()
        self.canvas.draw()

    def _style_axes(self, ax):
        ax.set_facecolor("#FFFFFF")
        ax.set_title(
            self._title, fontsize=12, fontweight="bold",
            color="#0F172A", pad=10
        )
        ax.set_xlabel(self._x_label, fontsize=10, color="#475569")
        ax.set_ylabel(self._y_label, fontsize=10, color="#475569")
        ax.tick_params(colors="#64748B", labelsize=9)
        ax.grid(True, linestyle="--", alpha=0.35, color="#CBD5E1",
                axis="x" if self._horizontal else "y")
        for spine in ax.spines.values():
            spine.set_edgecolor("#E2E8F0")
            spine.set_linewidth(0.8)

    def plot(
        self,
        labels:     list[str],
        values:     list[float],
        colors:     Optional[list[str]] = None,
        value_fmt:  str = "{:.1f}",
        bar_width:  float = 0.6,
    ):
        """
        Plot bar chart.

        labels     : label tiap bar
        values     : nilai tiap bar
        colors     : warna per bar (opsional, default pakai BAR_COLORS)
        value_fmt  : format angka yang ditampilkan di ujung bar
        """
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        self._style_axes(ax)

        n      = len(labels)
        colors = colors or [BAR_COLORS[i % len(BAR_COLORS)] for i in range(n)]
        x      = range(n)

        if self._horizontal:
            bars = ax.barh(x, values, height=bar_width, color=colors,
                           zorder=3, edgecolor="none")
            ax.set_yticks(list(x))
            ax.set_yticklabels(labels, fontsize=9)
            ax.set_xlabel(self._y_label, fontsize=10, color="#475569")
            ax.set_ylabel(self._x_label, fontsize=10, color="#475569")
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_width() + max(values) * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    value_fmt.format(val),
                    va="center", ha="left", fontsize=8, color="#334155"
                )
        else:
            bars = ax.bar(x, values, width=bar_width, color=colors,
                          zorder=3, edgecolor="none")
            ax.set_xticks(list(x))
            ax.set_xticklabels(labels, fontsize=9, rotation=15, ha="right")
            for bar, val in zip(bars, values):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(values) * 0.01,
                    value_fmt.format(val),
                    va="bottom", ha="center", fontsize=8, color="#334155"
                )

        self.figure.tight_layout()
        self.canvas.draw()

    def plot_risk_distribution(self, dist: dict[str, int]):
        """
        Shortcut: plot distribusi 4 risk tier dengan warna baku.
        dist = {"CRITICAL": 105, "HIGH": 34, "MEDIUM": 53, "LOW": 22}
        """
        tiers  = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        labels = tiers
        values = [dist.get(t, 0) for t in tiers]
        colors = [RISK_COLORS[t] for t in tiers]
        self.plot(labels, values, colors=colors, value_fmt="{:.0f}")

    def clear(self):
        self._draw_empty()