"""Hand actuator view"""
from typing import Optional

from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QAction, QLabel, QToolButton, QToolBar

from view.tool_button_style import build_tool_button


class HandActuator:
    """Hand actuator that contains the action and the webcam image label"""
    def __init__(self, tool_bar: QToolBar):
        self.tool_bar = tool_bar
        self.enabled: bool = False

        self.action = QAction()
        self.button: Optional[QToolButton()] = None
        self.on_icon = QIcon(QPixmap('./resources/webcam.png'))
        self.off_icon = QIcon(QPixmap('./resources/webcam_off.png'))
        self.build_button()

        self.actuator_image = QLabel()

    def set_pixmap(self, pixmap: QPixmap):
        """Pixmap setter"""
        self.actuator_image.setPixmap(pixmap)

    def set_visible(self, visible: bool):
        """Visibility setter"""
        self.enabled = visible
        self.set_icon()
        self.actuator_image.setVisible(visible)

    def get_actuator_image(self):
        """Actuator image getter"""
        return self.actuator_image

    def build_button(self):
        """Builds the button of the action"""
        self.button = build_tool_button(toolbar=self.tool_bar,
                                        action=self.action,
                                        button_text='Camera',
                                        icon_path='./resources/camera.png')
        self.set_icon()

    def set_icon(self):
        """Icon setter"""
        if self.enabled:
            self.button.setIcon(self.on_icon)
        else:
            self.button.setIcon(self.off_icon)
