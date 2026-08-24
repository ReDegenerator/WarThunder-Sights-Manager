import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSize

from src.views.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    css_path = os.path.join("src", "views", "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())