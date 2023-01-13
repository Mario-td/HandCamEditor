"""Resize action controller module"""
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QToolBar

from .editing_tool import EditingToolAction, ButtonContainer


class FilterAction(EditingToolAction):
    """Filter action controller"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_icon_path = './resources/filter.png'

        self.button_container = ButtonContainer(self.toolbar)

    def add_widgets_and_actions_to_toolbar(self):
        """Appends the elements to the toolbar"""
        self.button_container.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()

    def set_tool_button_icon(self):
        """QToolButton icon setter """
        self.button.setIcon(QIcon(QPixmap(self.button_icon_path).scaledToHeight(22)))
