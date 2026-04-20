from PyQt6.QtWidgets import QWidget, QSizePolicy
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from typing import Optional
from .layout import VBox
from .typography import Typography
from .colors import Colors


CLUSTER_COLORS = [
    "#2563EB",  # blue
    "#DC2626",  # red
    "#16A34A",  # green
    "#D97706",  # amber
    "#7C3AED",  # violet
    "#DB2777",  # pink
    "#0891B2",  # cyan
    "#EA580C",  # orange
]


class ScatterPlot(QWidget):
    def __init__(
        self,
        title: str = "Scatter Plot",
        x_label: str = "X",
        y_label: str = "Y",
        figsize: tuple[float, float] = (7, 5),
        parent=None,
    ):
        super().__init__(parent)

        self._title   = title
        self._x_label = x_label
        self._y_label = y_label

        layout = VBox(spacing=0)
        self.setLayout(layout)

        self.figure  = Figure(figsize=figsize, dpi=100, facecolor="#F8FAFC")
        self.canvas  = FigureCanvas(self.figure)
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
        ax.tick_params(colors="#64748B", labelsize=9)
        ax.grid(True, linestyle="--", alpha=0.4, color="#CBD5E1")
        for spine in ax.spines.values():
            spine.set_edgecolor("#E2E8F0")
        self.figure.tight_layout()
        self.canvas.draw()

    def plot(
        self,
        points: list[list[float]],          # [[x, y], ...]
        labels: list[int],                   # cluster index per point
        annotations: Optional[list[str]] = None,  # label per point
        n_clusters: Optional[int] = None,
    ):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#FFFFFF")

        n_clusters = n_clusters or (max(labels) + 1 if labels else 0)

        for c in range(n_clusters):
            idx = [j for j, lbl in enumerate(labels) if lbl == c]
            xs  = [points[j][0] for j in idx]
            ys  = [points[j][1] for j in idx]

            color = CLUSTER_COLORS[c % len(CLUSTER_COLORS)]
            ax.scatter(
                xs, ys,
                color=color,
                label=f"Cluster {c}",
                s=90,
                edgecolors="#FFFFFF",
                linewidths=0.6,
                zorder=3,
            )

            if annotations:
                for j in idx:
                    ax.annotate(
                        annotations[j],
                        (points[j][0], points[j][1]),
                        fontsize=7,
                        ha="left", va="bottom",
                        xytext=(5, 5),
                        textcoords="offset points",
                        color="#334155",
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