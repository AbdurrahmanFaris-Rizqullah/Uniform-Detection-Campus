from PyQt5.QtWidgets import QApplication
from src.ui.drawing_window import DrawingWindow
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DrawingWindow()
    window.show()
    sys.exit(app.exec_())