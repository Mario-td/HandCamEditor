"""Menu bar view module"""
from PyQt5.QtWidgets import QWidget, QSizePolicy, QToolBar


class MenuBar(QToolBar):
    """Menu bar view"""
    def __init__(self):
        super().__init__('Menu Bar')
        self.setMovable(False)

        self.right_spacer_menu_bar = QWidget()
        self.right_spacer_menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.right_spacer_menu_bar.setVisible(True)

    def fix_actions_to_left(self):
        """Fixes the actions on the left side"""
        self.addWidget(self.right_spacer_menu_bar)
