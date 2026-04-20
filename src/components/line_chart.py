from PyQt6.QtWidgets import QWidget, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import Optional
from .layout import VBox


LINE_COLORS = [
    "#2563EB",
    "#DC2626",
    "#16A34A",
    "#D97706",
    "#7C3AED",
]


class LineChart(QWidget):
    def __init__(
        self,
        title: str = "Line Chart",
        x_label: str = "X",
        y_label: str = "Y",
        figsize: tuple[float, float] = (7, 4),
        parent=None,
    ):
        super().__init__(parent)

        self._title   = title
        self._x_label = x_label
        self._y_label = y_label

        layout = VBox(spacing=0)
        self.setLayout(layout)

        self.figure = Figure(figsize=figsize, dpi=100, facecolor="#F8FAFC")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout.addWidget(self.canvas)
        self._draw_empty()

    def _draw_empty(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#F8FAFC")
        ax.set_title(self._title, fontsize=13, fontweight="bold", color="#0F172A", pad=12)
        ax.set_xlabel(self._x_label, fontsize=10, color="#475569")
        ax.set_ylabel(self._y_label, fontsize=10, color="#475569")
        ax.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
        for spine in ax.spines.values():
            spine.set_edgecolor("#E2E8F0")
        self.figure.tight_layout()
        self.canvas.draw()

    def plot(
        self,
        series: list[dict],
        # series = [
        #   { "label": "J", "x": [1, 2, 3, ...], "y": [0.5, 0.3, ...] },
        # ]
        markers: bool = True,
    ):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        for idx, s in enumerate(series):
            color  = LINE_COLORS[idx % len(LINE_COLORS)]
            marker = "o" if markers else None
            ax.plot(
                s["x"], s["y"],
                label=s.get("label", f"Series {idx}"),
                color=color,
                linewidth=2,
                marker=marker,
                markersize=5,
                zorder=3,
            )

        ax.set_title(self._title, fontsize=13, fontweight="bold", color="#0F172A", pad=12)
        ax.set_xlabel(self._x_label, fontsize=10, color="#475569")
        ax.set_ylabel(self._y_label, fontsize=10, color="#475569")
        ax.tick_params(colors="#64748B", labelsize=9)
        ax.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
        ax.legend(fontsize=9, framealpha=0.8)
        for spine in ax.spines.values():
            spine.set_edgecolor("#E2E8F0")

        self.figure.tight_layout()
        self.canvas.draw()

    def clear(self):
        self._draw_empty()