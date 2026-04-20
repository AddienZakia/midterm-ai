import os
from PyQt6.QtGui import QFontDatabase

class Fonts:
    def __init__(self, path_dir: str = "assets/fonts"):
        self.path_dir = path_dir

    def load_fonts(self):
        loc_fonts = os.listdir("assets/fonts")
        for font in loc_fonts:
            QFontDatabase.addApplicationFont(os.path.join("assets/fonts", font))

