"""Image viewer controller module"""
from PyQt5.QtCore import pyqtSignal, QObject


class ImageViewerController(QObject):
    """Controller of the element that displays the image that is edited"""
    def __init__(self, view, model):
        super().__init__()
        self.image_viewer = view.image_viewer
        self.model = model

    image_changed = pyqtSignal()

    def display_image(self, get_pixmap=None):
        """Displays the image given a pixmap getter function"""
        if get_pixmap is None:
            self.image_viewer.display_image(self.model.get_temp_pixmap())
        else:
            self.image_viewer.display_image(get_pixmap())
        self.image_changed.emit()
