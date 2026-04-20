from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from dataclasses import dataclass
from typing import Literal
from .colors import Colors
from ..utils import Fonts


TypographyVariant = Literal["h1", "h2", "h3", "h4", "h5", "h6", "t", "p", "b", "c"]
FontWeight = Literal["regular", "medium", "bold"]


@dataclass(frozen=True)
class TypographyConfig:
    font_size: int
    line_height: float


VARIANT_CONFIG: dict[str, TypographyConfig] = {
    "h1": TypographyConfig(font_size=32, line_height=1.2),
    "h2": TypographyConfig(font_size=28, line_height=1.2),
    "h3": TypographyConfig(font_size=24, line_height=1.25),
    "h4": TypographyConfig(font_size=20, line_height=1.3),
    "h5": TypographyConfig(font_size=18, line_height=1.3),
    "h6": TypographyConfig(font_size=16, line_height=1.4),
    "t":  TypographyConfig(font_size=15, line_height=1.4),
    "p":  TypographyConfig(font_size=14, line_height=1.5),
    "b":  TypographyConfig(font_size=13, line_height=1.5),
    "c":  TypographyConfig(font_size=12, line_height=1.4),
}

WEIGHT_MAP: dict[str, int] = {
    "regular": QFont.Weight.Normal,
    "medium":  QFont.Weight.Medium,
    "bold":    QFont.Weight.Bold,
}


class Typography(QLabel):
    def __init__(
        self,
        text: str = "",
        variant: TypographyVariant = "p",
        weight: FontWeight = "regular",
        color: str = Colors.neutral_black,
        align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft,
        word_wrap: bool = False,
        parent=None,
    ):
        super().__init__(text, parent)

        self.variant = variant
        self.weight = weight
        self._color = color

        config = VARIANT_CONFIG[variant]

        loc_font = Fonts()
        loc_font.load_fonts()

        font = QFont("Plus Jakarta Sans")
        font.setPointSize(config.font_size)
        font.setWeight(WEIGHT_MAP[weight])
        self.setFont(font)

        self.setAlignment(align)
        self.setWordWrap(word_wrap)
        self._apply_style()

    def _apply_style(self):
        config = VARIANT_CONFIG[self.variant]
        self.setStyleSheet(f"""
            QLabel {{
                color: {self._color};
                line-height: {config.line_height};
                background: transparent;
            }}
        """)

    def set_color(self, color: str):
        self._color = color
        self._apply_style()