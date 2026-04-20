import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QSizePolicy
from PyQt6.QtCore import Qt
from src.components import Typography, VBox, Colors
from .components import Button
from .utils import Fonts

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FCM Clustering App")
        self.setFixedSize(1000, 750)

        central = QWidget()
        central.setStyleSheet(f"background-color: {Colors.neutral_10};")
        layout = VBox()
        central.setLayout(layout)

        placeholder = Typography(
            "FCM Clustering — coming soon",
            variant="h5",
            color=Colors.neutral_50,
            align=Qt.AlignmentFlag.AlignCenter,
            weight="bold"
        )

        layout.addWidget(button)
        layout.addWidget(placeholder)

        self.setCentralWidget(central)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    Fonts().load_fonts()

    win = MainWindow()
    win.show()
    sys.exit(app.exec())
