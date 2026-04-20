from PyQt6.QtWidgets import (
    QWidget, QLabel, QFileDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from typing import Optional
from .layout import VBox
from .typography import Typography
from .colors import Colors


class UploadFile(QWidget):
    file_selected = pyqtSignal(str)  # emit path string

    def __init__(
        self,
        accept: str = "CSV Files (*.csv)",
        placeholder: str = "Drag & drop file here, or click to browse",
        height: int = 120,
        parent=None,
    ):
        super().__init__(parent)

        self.accept       = accept
        self._file_path: Optional[str] = None

        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = VBox(spacing=6, align=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.icon_label = Typography("📂", variant="h4", align=Qt.AlignmentFlag.AlignCenter)
        self.text_label = Typography(
            placeholder, variant="b",
            color=Colors.neutral_60,
            align=Qt.AlignmentFlag.AlignCenter,
        )
        self.file_label = Typography(
            "", variant="c",
            color=Colors.primary_main,
            align=Qt.AlignmentFlag.AlignCenter,
        )

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        layout.addWidget(self.file_label)

        self._apply_style(active=False)

    def _apply_style(self, active: bool = False):
        border_color = Colors.primary_main if active else Colors.neutral_40
        bg_color     = Colors.neutral_10 if not active else "#EFF6FF"
        self.setStyleSheet(f"""
            UploadFile {{
                border:        2px dashed {border_color};
                border-radius: 8px;
                background:    {bg_color};
            }}
            UploadFile:hover {{
                border-color:  {Colors.primary_main};
                background:    #EFF6FF;
            }}
        """)

    # ── mouse click ──────────────────────────────────────────────
    def mousePressEvent(self, event):
        self._open_dialog()

    def _open_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select File", "", self.accept)
        if path:
            self._set_file(path)

    # ── drag & drop ──────────────────────────────────────────────
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._apply_style(active=True)

    def dragLeaveEvent(self, event):
        self._apply_style(active=bool(self._file_path))

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            self._set_file(path)

    # ── internal ─────────────────────────────────────────────────
    def _set_file(self, path: str):
        self._file_path = path
        file_name = path.split("/")[-1]
        self.file_label.setText(f"✓  {file_name}")
        self._apply_style(active=True)
        self.file_selected.emit(path)

    def get_path(self) -> Optional[str]:
        return self._file_path

    def reset(self):
        self._file_path = None
        self.file_label.setText("")
        self._apply_style(active=False)