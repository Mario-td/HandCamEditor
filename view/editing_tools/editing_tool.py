"""Editing tool controller module"""
from abc import abstractmethod
from typing import Optional, Callable

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QHBoxLayout, QWidget, \
    QToolBar, QScrollArea, QScrollBar, QPushButton, QToolButton, QSizePolicy

from view.accept_cancel import AcceptCancelContainer
from view.tool_button_style import BUTTON_WIDTH, BUTTON_HEIGHT


class EditingToolAction(QAction):
    """Abstract class of the editing tools"""

    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text)
        self.toolbar = toolbar
        self.button_text = text
        self.button_icon_path: Optional[str] = None
        self.button: Optional[QToolButton] = None
        self.build_tool_button()

        self.accept_and_cancel = AcceptCancelContainer(self.toolbar)

    @abstractmethod
    def add_widgets_and_actions_to_toolbar(self):
        """Add the elements to the editing toolbar"""

    def set_tool_button_icon(self):
        """QToolButton icon setter """
        self.button.setIcon(QIcon(QPixmap(self.button_icon_path)))

    def display_items(self):
        """Displays the items in the toolbar"""
        self.toolbar.clear()
        self.add_widgets_and_actions_to_toolbar()

    def build_tool_button(self):
        """Builds the button and resets the configuration"""
        self.button = QToolButton()
        self.button.setText(self.button_text)
        self.button.clicked.connect(self.trigger)
        self.button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button.installEventFilter(self.toolbar)
        self.set_tool_button_icon()


class Tool:
    """Superclass for the tool components"""

    def __init__(self, toolbar: QToolBar):
        super().__init__()
        self.toolbar = toolbar

        self.tools_layout = QHBoxLayout()
        self.tools_container = QWidget()
        self.tools_container.setLayout(self.tools_layout)
        self.tools_container.setObjectName('button-container')

    def add_widgets_and_actions_to_toolbar(self):
        """Adds the elements to the toolbar"""
        self.tools_container.setVisible(True)
        self.toolbar.addWidget(self.tools_container)

    @abstractmethod
    def build_buttons(self):
        """Builds the buttons of the actions"""


class ButtonContainer(Tool):
    """Contains the buttons and the arrows to scroll"""

    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)

        self.move_scroll_area_left_action = QAction()
        self.move_scroll_area_left_action \
            .setIcon(QIcon(QPixmap('./resources/left_arrow.png').scaledToHeight(30)))
        self.move_scroll_area_right_action = QAction()
        self.move_scroll_area_right_action \
            .setIcon(QIcon(QPixmap('./resources/right_arrow.png').scaledToHeight(30)))

        self.tools_layout.setContentsMargins(0, 5, 0, 0)
        self.buttons: list = []
        self.scroll_area = QScrollArea()
        self.scrollbar = QScrollBar()
        self.scrollbar.setFixedSize(0, 0)
        self.scrollbar.setObjectName("FilterScrollbar")
        self.scroll_area.setHorizontalScrollBar(self.scrollbar)
        self.scroll_area.setWidgetResizable(True)

    def add_widgets_and_actions_to_toolbar(self):
        """Appends the elements to the toolbar"""
        self.scroll_area.setVisible(True)
        self.toolbar.addAction(self.move_scroll_area_left_action)
        self.toolbar.addWidget(self.scroll_area)
        self.toolbar.addAction(self.move_scroll_area_right_action)

    def populate_buttons(self, number_buttons):
        """Appends all the buttons to the container"""
        for _ in range(number_buttons):
            button = QPushButton()
            button.setIconSize(QSize(80, 80))
            button.setFixedSize(QSize(90, 83))

            self.buttons.append(button)
            self.tools_layout.addWidget(button)
        self.scroll_area.setWidget(self.tools_container)

    def update_button_image(self, images):
        """Updates the image of the buttons"""
        for i, (name, img) in enumerate(images.items()):
            icon = QIcon(img)
            self.buttons[i].setIcon(icon)
            self.buttons[i].setToolTip(name)

    def build_buttons(self):
        pass


def center_widgets_in_toolbar(add_widgets: Callable) -> Callable:
    """Adds widgets on both sides of the toolbar to center it"""
    def wrapper(editing_tool_action: EditingToolAction):
        left_spacer_menu_bar = QWidget()
        left_spacer_menu_bar.setVisible(True)
        left_spacer_menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        editing_tool_action.toolbar.addWidget(left_spacer_menu_bar)

        add_widgets(editing_tool_action)

        right_spacer_menu_bar = QWidget()
        right_spacer_menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_spacer_menu_bar.setVisible(True)
        editing_tool_action.toolbar.addWidget(right_spacer_menu_bar)

    return wrapper
