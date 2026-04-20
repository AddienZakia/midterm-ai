import os, sys
from PyQt6.QtGui import QFontDatabase

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class Fonts:
    def __init__(self, path_dir: str = "assets/fonts"):
        self.path_dir = path_dir

    def load_fonts(self):
        loc_fonts = os.listdir(resource_path("assets/fonts"))
        for font in loc_fonts:
            QFontDatabase.addApplicationFont(os.path.join("assets/fonts", font))

