"""Deep Dream  view file"""
from typing import Optional, List, Dict
from PyQt5.QtWidgets import QToolBar, QAction, QToolButton

from view.editing_tools import EditingToolAction
from view.editing_tools.editing_tool import Tool, center_widgets_in_toolbar
from view.tool_button_style import build_tool_button


class DeepDreamAction(EditingToolAction):
    """Deep Dream action view class"""

    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_icon_path = './resources/deep_dream.png'
        self.button_text = 'Dream'

        self.deep_dream_tools = DeepDreamTools(self.toolbar)

    @center_widgets_in_toolbar
    def add_widgets_and_actions_to_toolbar(self):
        self.deep_dream_tools.add_widgets_and_actions_to_toolbar()
        self.accept_and_cancel.add_actions_to_toolbar()


# pylint: disable=R0902
class DeepDreamTools(Tool):
    """Tools of the Deep Dream action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)
        self.dreams_list: List[QAction] = []
        self.buttons: Dict[str, QToolButton] = {}

        self.curly_action = QAction('Curly')
        self.dreams_list.append(self.curly_action)
        self.curly_button: Optional[QToolButton] = None

        self.stripes_action = QAction('Stripes')
        self.dreams_list.append(self.stripes_action)
        self.stripes_button: Optional[QToolButton] = None

        self.shapes_action = QAction('Shapes')
        self.dreams_list.append(self.shapes_action)
        self.shapes_button: Optional[QToolButton] = None

        self.holes_action = QAction('Holes')
        self.dreams_list.append(self.holes_action)
        self.holes_button: Optional[QToolButton] = None

        self.random_action = QAction('Random')
        self.dreams_list.append(self.random_action)
        self.random_button: Optional[QToolButton] = None

    def add_widgets_and_actions_to_toolbar(self):
        self.build_buttons()
        self.toolbar.addWidget(self.holes_button)
        self.toolbar.addWidget(self.curly_button)
        self.toolbar.addWidget(self.shapes_button)
        self.toolbar.addWidget(self.stripes_button)
        self.toolbar.addWidget(self.random_button)

    def build_buttons(self):
        self.curly_button = build_tool_button(toolbar=self.toolbar,
                                              action=self.curly_action,
                                              button_text='Curly',
                                              icon_path='./resources/curly.png',
                                              size=(0, 30))
        self.buttons[self.curly_button.text()] = self.curly_button

        self.stripes_button = build_tool_button(toolbar=self.toolbar,
                                                action=self.stripes_action,
                                                button_text='Stripes',
                                                icon_path='./resources/stripes.png',
                                                size=(0, 30))
        self.buttons[self.stripes_button.text()] = self.stripes_button

        self.shapes_button = build_tool_button(toolbar=self.toolbar,
                                               action=self.shapes_action,
                                               button_text='Shapes',
                                               icon_path='./resources/shapes.png',
                                               size=(0, 30))
        self.buttons[self.shapes_button.text()] = self.shapes_button

        self.holes_button = build_tool_button(toolbar=self.toolbar,
                                              action=self.holes_action,
                                              button_text='Holes',
                                              icon_path='./resources/holes.png',
                                              size=(0, 30))
        self.buttons[self.holes_button.text()] = self.holes_button

        self.random_button = build_tool_button(toolbar=self.toolbar,
                                               action=self.random_action,
                                               button_text='Random',
                                               icon_path='./resources/random.png',
                                               size=(0, 30))
        self.buttons[self.random_button.text()] = self.random_button
