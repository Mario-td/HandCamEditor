"""Entry point file"""
import sys

from view import MainWindow
from controller import MainController
from model import ImageEditor


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import pyqtRemoveInputHook
    pyqtRemoveInputHook()
    with open('stylesheet.qss', 'r') as file:
        app = QApplication(sys.argv)
        app.setStyleSheet(file.read())
        app.setApplicationName('HandCamEditor')
        main_window = MainWindow()
        main_window.show()
        image_editor = ImageEditor()
        MainController(view=main_window, model=image_editor)
        sys.exit(app.exec())
