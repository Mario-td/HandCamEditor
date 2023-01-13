"""Utils for the toolbutton style"""
from typing import Tuple

from PyQt5.QtCore import QEvent, QObject, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QToolButton, QToolBar, QAction

BUTTON_WIDTH = 80
BUTTON_HEIGHT = 60


# pylint: disable=C0103
def eventFilter(obj: QToolButton, event: QEvent) -> bool:
    """Sets the icon over the text when it's hovered"""
    if event.type() == QEvent.HoverEnter:
        obj.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
    if event.type() == QEvent.HoverLeave:
        obj.setToolButtonStyle(Qt.ToolButtonIconOnly)
    return QObject.event(obj, event)


def build_tool_button(toolbar: QToolBar, action: QAction,
                      button_text: str, icon_path: str = '',
                      size: Tuple[int, int] = (0, 0)) -> QToolButton:
    """Builds a QToolButton given some features"""
    button = QToolButton()
    if size[0] and size[1]:
        button.setIcon(QIcon(QPixmap(icon_path).scaled(size[0], size[1])))
    elif size[1]:
        button.setIcon(QIcon(QPixmap(icon_path).scaledToHeight(size[1])))
    elif size[0]:
        button.setIcon(QIcon(QPixmap(icon_path).scaledToWidth(size[0])))
    else:
        button.setIcon(QIcon(QPixmap(icon_path)))

    button.setText(button_text)
    button.clicked.connect(action.trigger)
    button.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
    button.installEventFilter(toolbar)
    return button
