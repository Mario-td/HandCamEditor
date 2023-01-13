"""Rotate action controller module"""
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QMessageBox, QAction

from view.editing_tools.rotation import RotateTools, RotateAction
from .editing_tool import EditingTool
from ..image_viewer import ImageViewerController


class RotateActionController(EditingTool):
    """Controller of the rotate action"""
    def __init__(self, view, model, rotate_action: RotateAction):
        super().__init__(view, model, rotate_action)
        self.view = view
        self.model = model

        self.rotate_tools_controller = RotateToolsController(self, rotate_action.rotate_tools)

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to rotate')
            return
        self.model.create_temp_image()
        self.action.display_items()


class RotateToolsController(QObject):
    """Controller of the rotate tools"""
    def __init__(self, rotate_action_controller: RotateActionController, rotate_tools: RotateTools):
        super().__init__()
        self.image_viewer_controller = \
            ImageViewerController(rotate_action_controller.view, rotate_action_controller.model)
        self.rotate_tools = rotate_tools
        self.rotate_action_controller = rotate_action_controller
        self.rotation_model = self.image_viewer_controller.model.actions['Rotation']
        self.connect_action_to_signal(self.rotate_tools.rotate_right_action)
        self.connect_action_to_signal(self.rotate_tools.rotate_left_action)
        self.connect_action_to_signal(self.rotate_tools.vertical_flip_action)
        self.connect_action_to_signal(self.rotate_tools.horizontal_flip_action)

        self.connect_signal()

    rotate_signal = pyqtSignal(str)

    def connect_action_to_signal(self, action: QAction):
        """Connects all the actions to the signal:::"""
        text = action.text()
        action.triggered.connect(lambda: self.emit_signal_and_update_image(text))

    def emit_signal_and_update_image(self, text):
        """Triggers the signal and updates the display"""
        self.rotate_signal.emit(text)
        self.image_viewer_controller.\
            display_image(self.image_viewer_controller.model.get_temp_pixmap)
        self.rotate_action_controller.accept_action.setDisabled(False)

    def connect_signal(self):
        """Connects the rotation actions signal with the model"""
        self.rotate_signal.connect(self.rotation_model.rotate_temp_image)
