"""Adjust view file"""
from typing import Dict, List

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QToolBar, QSlider, QAction, QToolButton

from view.editing_tools import EditingToolAction
from view.editing_tools.editing_tool import Tool, center_widgets_in_toolbar
from view.tool_button_style import build_tool_button


class AdjustAction(EditingToolAction):
    """Adjust action view class"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_icon_path = './resources/adjust.png'

        self.adjust_tools = AdjustTools(self.toolbar)

    @center_widgets_in_toolbar
    def add_widgets_and_actions_to_toolbar(self):
        self.adjust_tools.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()


class AdjustTools(Tool):
    """Tools of the Adjust action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)

        self.adjustable_features: List[QAction] = []
        self.feature_buttons: Dict[str, QToolButton] = {}
        self.add_feature('Brightness', './resources/brightness.png')
        self.add_feature('Contrast', './resources/contrast.png')
        self.add_feature('Saturation', './resources/saturation.png', 30)
        self.add_feature('Sharpness', './resources/sharpness.png', 30)

        self.features_slider = QSlider(Qt.Horizontal)

    def add_widgets_and_actions_to_toolbar(self):
        self.build_buttons()
        for button in self.feature_buttons.values():
            self.toolbar.addWidget(button)
        self.features_slider = QSlider(Qt.Horizontal)
        self.features_slider.setMinimumWidth(160)
        self.features_slider.setFixedHeight(20)
        self.toolbar.addWidget(self.features_slider)

    def add_feature(self, feature_name: str, icon_path: str = '', height: int = 26):
        """Adds a feature action"""
        action = QAction(feature_name)
        if icon_path:
            action.setIcon(QIcon(QPixmap(icon_path).scaledToHeight(height)))
        self.adjustable_features.append(action)

    def build_buttons(self):
        for action in self.adjustable_features:
            button = build_tool_button(toolbar=self.toolbar,
                                       action=action,
                                       button_text=action.text())

            icon: QIcon = action.icon()
            button.setIcon(icon)
            self.feature_buttons[action.text()] = button
