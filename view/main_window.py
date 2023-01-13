"""Main window view module"""
from PyQt5.QtWidgets import QMainWindow, QGridLayout, \
    QWidget

from .editing_bar import EditingToolBar
from .image_viewer import ImageViewer


# pylint: disable=R0902
# pylint: disable=C0103
class MainWindow(QMainWindow):
    """Main window of the application"""

    def __init__(self):
        super().__init__()
        self.showMaximized()

        self.image_viewer = ImageViewer()

        self.tool_bar = EditingToolBar()
        self.addToolBar(self.tool_bar)

        self.central_layout = QGridLayout()
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setHorizontalSpacing(12)

        self.central_layout.addWidget(self.image_viewer.image_view, 0, 0, 6, 6)
        self.central_widget = QWidget()
        self.central_widget.setObjectName('central-widget')

        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

    def new_image_ui_setup(self):
        """Sets the view of the elements when there is a new image"""
        self.tool_bar.new_image_setup()

    def restored_ui_setup(self):
        """Default view setup"""
        self.tool_bar.refresh()
