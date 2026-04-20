from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import Qt
from typing import Optional


class VBox(QVBoxLayout):
    def __init__(
        self,
        spacing: int = 8,
        margin: tuple[int, int, int, int] = (0, 0, 0, 0),
        align: Optional[Qt.AlignmentFlag] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.setSpacing(spacing)
        self.setContentsMargins(*margin)

        if align is not None:
            self.setAlignment(align)


class HBox(QHBoxLayout):
    def __init__(
        self,
        spacing: int = 8,
        margin: tuple[int, int, int, int] = (0, 0, 0, 0),
        align: Optional[Qt.AlignmentFlag] = None,
        parent=None,
    ):
        super().__init__(parent)

        self.setSpacing(spacing)
        self.setContentsMargins(*margin)

        if align is not None:
            self.setAlignment(align)