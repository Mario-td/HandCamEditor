"""Main controller module"""
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QRegExp
from .editing_bar import EditingToolBarController
from .image_viewer import ImageViewerController
from .hand_actuator import HandActuatorController


class MainController:
    """Controller of the main window"""
    def __init__(self, view, model):
        self.image_viewer_controller = ImageViewerController(view, model)

        self.view = view
        self.model = model

        self.hand_actuator_controller = HandActuatorController(view,
                                                               view.tool_bar.
                                                               get_hand_actuator_view())

        self.editing_tool_bar_controller = EditingToolBarController(view, model,
                                                                    view.tool_bar)
        self.connect_menu_bar_signals()

    def open_image(self):
        """Opens a new image"""
        dialog = QFileDialog()
        dialog.setWindowTitle('Open Image')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('Images (*.png *.bmp *.jpg)')
        if dialog.exec():
            file_path = dialog.selectedFiles()
            self.model.load_image((file_path[0]))
            self.view.new_image_ui_setup()
            self.image_viewer_controller.display_image(self.model.get_current_pixmap)

    def save_image_as(self):
        """Saves the image"""
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to save')
            return
        dialog = QFileDialog()
        dialog.setWindowTitle('Save Image As...')
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setNameFilter('Images (*.png *.bmp *.jpg)')
        if dialog.exec():
            file_path = dialog.selectedFiles()
            if QRegExp('.+\\.(png|bmp|jpg)').exactMatch(file_path[0]):
                self.model.save_image_as(file_path[0])
                return
            QMessageBox(self.view).information(self.view,
                                               'Information',
                                               'Not saved: invalid format or filename')

    def connect_menu_bar_signals(self):
        """Connects signals with slots"""
        self.view.tool_bar.get_open_image_action().triggered.connect(lambda: self.open_image())
        self.view.tool_bar.get_save_image_action().triggered.connect(lambda: self.save_image_as())
