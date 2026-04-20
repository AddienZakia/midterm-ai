from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class Image(QLabel):
    def __init__(self, path, width=None, height=None):
        super().__init__()

        pixmap = QPixmap(path)

        if width and height:
            pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)

        self.setPixmap(pixmap)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)