from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QCursor
from typing import Literal, Optional
from .colors import Colors


ButtonVariant = Literal["primary", "success", "warning", "error", "alternative", "outlined"]
ButtonSize    = Literal["sm", "md", "lg"]


_VARIANT_STYLE: dict[str, dict] = {
    "primary": {
        "bg":              Colors.primary_main,
        "bg_hover":        Colors.primary_hover,
        "bg_active":       Colors.primary_active,
        "bg_disabled":     Colors.primary_active,
        "text":            Colors.neutral_white,
        "text_disabled":   Colors.neutral_white,
        "border":          "none",
        "border_disabled": f"1px solid {Colors.primary_active}",
    },
    "success": {
        "bg":              Colors.success_main,
        "bg_hover":        Colors.success_hover,
        "bg_active":       Colors.success_active,
        "bg_disabled":     Colors.neutral_30,
        "text":            Colors.neutral_white,
        "text_disabled":   Colors.neutral_60,
        "border":          "none",
        "border_disabled": f"1px solid {Colors.neutral_60}",
    },
    "warning": {
        "bg":              Colors.warning_main,
        "bg_hover":        Colors.warning_hover,
        "bg_active":       Colors.warning_active,
        "bg_disabled":     Colors.neutral_30,
        "text":            Colors.neutral_white,
        "text_disabled":   Colors.neutral_60,
        "border":          "none",
        "border_disabled": f"1px solid {Colors.neutral_60}",
    },
    "error": {
        "bg":              Colors.error_main,
        "bg_hover":        Colors.error_hover,
        "bg_active":       Colors.error_active,
        "bg_disabled":     Colors.error_active,
        "text":            Colors.neutral_white,
        "text_disabled":   Colors.neutral_60,
        "border":          "none",
        "border_disabled": f"1px solid {Colors.neutral_60}",
    },
    "alternative": {
        "bg":              Colors.neutral_80,
        "bg_hover":        Colors.neutral_70,
        "bg_active":       Colors.neutral_90,
        "bg_disabled":     Colors.neutral_30,
        "text":            Colors.neutral_white,
        "text_disabled":   Colors.neutral_60,
        "border":          "none",
        "border_disabled": f"1px solid {Colors.neutral_60}",
    },
    "outlined": {
        "bg":              Colors.neutral_10,
        "bg_hover":        Colors.neutral_30,
        "bg_active":       Colors.neutral_40,
        "bg_disabled":     Colors.neutral_30,
        "text":            Colors.neutral_black,
        "text_disabled":   Colors.neutral_60,
        "border":          f"1px solid {Colors.neutral_60}",
        "border_disabled": f"1px solid {Colors.neutral_60}",
    },
}

_SIZE_STYLE: dict[str, dict] = {
    "sm": {"padding": "6px 16px", "font_size": 14},
    "md": {"padding": "8px 16px", "font_size": 16},
    "lg": {"padding": "10px 16px", "font_size": 16},
}


class Button(QPushButton):
    def __init__(
        self,
        text: str = "",
        variant: ButtonVariant = "primary",
        size: ButtonSize = "md",
        left_icon: Optional[QIcon] = None,
        right_icon: Optional[QIcon] = None,
        parent=None,
    ):
        super().__init__(text, parent)

        self.variant = variant
        self._size   = size

        if left_icon:
            self.setIcon(left_icon)
            self.setIconSize(QSize(16, 16))

        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._apply_style()

    def _apply_style(self):
        v = _VARIANT_STYLE[self.variant]
        s = _SIZE_STYLE[self._size]

        border          = v["border"] or "none"
        border_disabled = v["border_disabled"] or "none"
        
        font = QFont("Plus Jakarta Sans", s["font_size"])
        font.setWeight(QFont.Weight.Medium)
        self.setFont(font)

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {v["bg"]};
                color:            {v["text"]};
                border:           {border};
                border-radius:    6px;
                padding:          {s["padding"]};
                font-size:        {s["font_size"]}px;
                font-family: "Plus Jakarta Sans";
                font-weight:      500;
            }}
            QPushButton:hover {{
                background-color: {v["bg_hover"]};
            }}
            QPushButton:pressed {{
                background-color: {v["bg_active"]};
            }}
            QPushButton:disabled {{
                background-color: {v["bg_disabled"]};
                color:            {v["text_disabled"]};
                border:           {border_disabled};
                cursor:           not-allowed;
            }}
        """)
        