"""Backward Forwards Actions View"""
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QActionGroup


class BackwardsForwardsActions:
    """Backwards Forwards Actions Container"""
    def __init__(self):
        self.backwards_action = QAction('<=')
        self.backwards_action.setDisabled(True)
        enabled_icon = QPixmap('./resources/undo.png')
        disabled_icon = QPixmap('./resources/undo_disabled.png')
        icon = QIcon(enabled_icon)
        icon.addPixmap(disabled_icon, QIcon.Disabled)
        self.backwards_action.setIcon(icon)

        self.forwards_action = QAction('=>')
        self.forwards_action.setDisabled(True)
        enabled_icon = QPixmap('./resources/redo.png')
        disabled_icon = QPixmap('./resources/redo_disabled.png')
        icon = QIcon(enabled_icon)
        icon.addPixmap(disabled_icon, QIcon.Disabled)
        self.forwards_action.setIcon(icon)

        # empty means that both actions are disabled, l means left is enabled,
        # r means right is enabled, b means both are enabled
        self.state = ''

    def __call__(self, toolbar, *args, **kwargs):
        action_group = QActionGroup(toolbar)
        action_group.addAction(self.backwards_action)
        action_group.addAction(self.forwards_action)
        return action_group

    def add_actions_to_group(self, action_group):
        """Adds both actions to compact them"""
        action_group.addAction(self.backwards_action)
        action_group.addAction(self.forwards_action)

    def new_image_setup(self):
        """Sets the state when a new image is load"""
        self.state = ''
        self.backwards_action.setDisabled(True)
        self.forwards_action.setDisabled(True)

    def update_state_view(self, state: str):
        """Updates the state when some action is undone or done"""
        self.state = state
        if self.state == '':
            self.backwards_action.setDisabled(True)
            self.forwards_action.setDisabled(True)
        elif self.state == 'l':
            self.backwards_action.setDisabled(False)
            self.forwards_action.setDisabled(True)
        elif self.state == 'r':
            self.backwards_action.setDisabled(True)
            self.forwards_action.setDisabled(False)
        else:
            self.backwards_action.setDisabled(False)
            self.forwards_action.setDisabled(False)
