"""Resize action view module"""
from PyQt5.QtGui import QIntValidator, QPixmap
from PyQt5.QtWidgets import QCheckBox, QSlider, QLineEdit, QLabel, QToolBar
from PyQt5.QtCore import Qt

from .editing_tool import EditingToolAction, Tool, center_widgets_in_toolbar

MAX_WIDTH = 5000
MAX_HEIGHT = 5000


class ResizeAction(EditingToolAction):
    """Resize action view"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_icon_path = './resources/resize.png'

        self.resize_tools = ResizeTools(toolbar)

    @center_widgets_in_toolbar
    def add_widgets_and_actions_to_toolbar(self):
        self.resize_tools.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()


class ResizeTools(Tool):
    """Tools of the resize action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)

        self.width_line_edit = QLineEdit()
        self.width_line_edit.setMaximumWidth(90)
        self.width_line_edit.setValidator(QIntValidator(1, MAX_WIDTH, None))

        self.height_line_edit = QLineEdit()
        self.height_line_edit.setMaximumWidth(90)
        self.height_line_edit.setValidator(QIntValidator(1, MAX_HEIGHT, None))

        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setMinimumWidth(160)
        self.size_slider.setRange(1, MAX_WIDTH)

        self.aspect_ratio_checkbox = QCheckBox('Aspect Ratio')
        self.aspect_ratio_checkbox.setChecked(True)

        self.tools_layout.addWidget(self.size_slider)
        self.tools_layout.addWidget(self.width_line_edit)
        x_label = QLabel('x')
        x_label.setPixmap(QPixmap('./resources/cancel.png').scaledToHeight(20))
        self.tools_layout.addWidget(x_label)
        self.tools_layout.addWidget(self.height_line_edit)
        self.tools_layout.addWidget(self.aspect_ratio_checkbox)

    def build_buttons(self):
        pass
