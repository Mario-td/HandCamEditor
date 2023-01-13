"""Accept and Cancel container view"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction


class AcceptCancelContainer:
    """Accept and cancel container in a toolbar"""
    def __init__(self, toolbar):
        self.toolbar = toolbar

        self.accept_action = QAction()
        enabled_icon = QPixmap('./resources/accept.png').scaledToHeight(26)
        disabled_icon = QPixmap('./resources/accept_disabled.png').scaledToHeight(26)
        icon = QIcon(enabled_icon)
        icon.addPixmap(disabled_icon, QIcon.Disabled)
        self.accept_action.setIcon(icon)
        self.accept_action.setShortcut(Qt.Key_Return)

        self.cancel_action = QAction()
        self.cancel_action.setIcon(QIcon(QPixmap('./resources/cancel.png').scaledToHeight(30)))
        self.cancel_action.setShortcut(Qt.Key_Escape)

    def add_actions_to_toolbar(self):
        """Adds actions to the toolbar"""
        self.accept_action.setDisabled(True)

        self.toolbar.addAction(self.accept_action)
        self.toolbar.addAction(self.cancel_action)

    def get_accept_action(self) -> QAction:
        """Accept action getter"""
        return self.accept_action

    def get_cancel_action(self) -> QAction:
        """Cancel action getter"""
        return self.cancel_action
