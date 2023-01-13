"""Rotate view"""
from typing import Optional

from PyQt5.QtWidgets import QToolBar, QAction, QToolButton

from .editing_tool import EditingToolAction, Tool, center_widgets_in_toolbar
from ..tool_button_style import build_tool_button


class RotateAction(EditingToolAction):
    """Rotate action view"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)

        self.rotate_tools = RotateTools(self.toolbar)

        self.button_icon_path = './resources/rotate_right.png'

    @center_widgets_in_toolbar
    def add_widgets_and_actions_to_toolbar(self):
        self.rotate_tools.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()


# pylint: disable=R0902
class RotateTools(Tool):
    """Tools of the resize action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)

        self.rotate_right_action = QAction('R')
        self.rotate_right_button: Optional[QToolButton] = None

        self.rotate_left_action = QAction('L')
        self.rotate_left_button: Optional[QToolButton] = None

        self.vertical_flip_action = QAction('V')
        self.vertical_flip_button: Optional[QToolButton] = None

        self.horizontal_flip_action = QAction('H')
        self.horizontal_flip_button: Optional[QToolButton] = None

    def add_widgets_and_actions_to_toolbar(self):
        self.build_buttons()
        self.toolbar.addWidget(self.rotate_left_button)
        self.toolbar.addWidget(self.rotate_right_button)
        self.toolbar.addWidget(self.vertical_flip_button)
        self.toolbar.addWidget(self.horizontal_flip_button)

    def build_buttons(self):
        self.rotate_right_button = build_tool_button(toolbar=self.toolbar,
                                                     action=self.rotate_right_action,
                                                     button_text='Right',
                                                     icon_path='./resources/rotate_right.png')
        self.rotate_left_button = build_tool_button(toolbar=self.toolbar,
                                                    action=self.rotate_left_action,
                                                    button_text='Left',
                                                    icon_path='./resources/rotate_left.png')
        self.vertical_flip_button = build_tool_button(toolbar=self.toolbar,
                                                      action=self.vertical_flip_action,
                                                      button_text='Vertical',
                                                      icon_path='./resources/flip_vertical.png')
        self.horizontal_flip_button = build_tool_button(toolbar=self.toolbar,
                                                        action=self.horizontal_flip_action,
                                                        button_text='Horizontal',
                                                        icon_path='./resources/flip_horizontal.png')
