import sys
sys.path.append('src')
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from ui.drawing_window import DrawingWindow

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    drawing_window = DrawingWindow()
    
    # Connect drawing window to main window
    main_window.open_drawing_btn.clicked.connect(drawing_window.show)
    
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()