"""Crop view file"""
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QToolBar, QLineEdit, QLabel

from .editing_tool import EditingToolAction, Tool, center_widgets_in_toolbar

MIN_WIDTH = 20
MIN_HEIGHT = 20


class CropAction(EditingToolAction):
    """Cropping action view class"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_icon_path = './resources/crop.png'

        self.crop_tools = CropTools(self.toolbar)

    @center_widgets_in_toolbar
    def add_widgets_and_actions_to_toolbar(self):
        self.crop_tools.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()


class CropTools(Tool):
    """Tools of the crop action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)

        self.width_line_edit = QLineEdit()
        self.width_line_edit.setMaximumWidth(90)
        self.width_line_edit.setValidator(QIntValidator(MIN_WIDTH, 999999, None))

        self.height_line_edit = QLineEdit()
        self.height_line_edit.setMaximumWidth(90)
        self.height_line_edit.setValidator(QIntValidator(MIN_HEIGHT, 999999, None))

        self.x_offset_line_edit = QLineEdit()
        self.x_offset_line_edit.setMaximumWidth(90)
        self.x_offset_line_edit.setValidator(QIntValidator(0, 999999, None))

        self.y_offset_line_edit = QLineEdit()
        self.y_offset_line_edit.setMaximumWidth(90)
        self.y_offset_line_edit.setValidator(QIntValidator(0, 999999, None))

        self.tools_layout.addWidget(self.width_line_edit)
        x_label = QLabel('X')
        x_label.setPixmap(QPixmap('./resources/cancel.png').scaledToHeight(20))
        self.tools_layout.addWidget(x_label)
        self.tools_layout.addWidget(self.height_line_edit)
        self.tools_layout.addWidget(QLabel('X-Offset:'))
        self.tools_layout.addWidget(self.x_offset_line_edit)
        self.tools_layout.addWidget(QLabel('Y-Offset:'))
        self.tools_layout.addWidget(self.y_offset_line_edit)

    def build_buttons(self):
        pass
