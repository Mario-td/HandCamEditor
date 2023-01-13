"""Style Transfer view file"""
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QToolBar, QAction, QPushButton

from view.editing_tools import EditingToolAction
from view.editing_tools.editing_tool import Tool, ButtonContainer


class StyleTransferAction(EditingToolAction):
    """Style Transfer action view class"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_text = 'Transfer'
        self.button_icon_path = './resources/style_transfer.png'
        self.style_transfer_tools = StyleTransferTools(self.toolbar)

    def add_widgets_and_actions_to_toolbar(self):
        self.style_transfer_tools.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()


class StyleTransferTools(Tool):
    """Tools of the Style Transfer action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)
        self.button_container = StyleImagesButtonContainerView(toolbar)
        self.add_styled_image_button = QAction()
        self.add_styled_image_button.setIcon(QIcon(QPixmap('./resources/add.png')
                                                   .scaledToHeight(30)))

    def add_widgets_and_actions_to_toolbar(self):
        self.button_container.add_widgets_and_actions_to_toolbar()
        self.toolbar.addAction(self.add_styled_image_button)

    def build_buttons(self):
        pass


class StyleImagesButtonContainerView(ButtonContainer):
    """Contains the style image buttons and the arrows to scroll"""
    def add_button(self, name, image):
        """Adds a new button"""
        button = QPushButton()
        button.setIconSize(QSize(80, 80))
        button.setFixedSize(QSize(90, 83))
        icon = QIcon(image)
        button.setIcon(icon)
        button.setToolTip(name)

        self.buttons.append(button)
        self.tools_layout.addWidget(button)
