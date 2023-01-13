"""Editing toolbar view"""
import dataclasses
from typing import Optional, Dict, List

from PyQt5.QtWidgets import QToolBar, QActionGroup, QWidget, \
    QSizePolicy, QAction, QToolButton

from .editing_tools import FilterAction, ResizeAction, \
    CropAction, EditingToolAction, RotateAction, DeepDreamAction
from .editing_tools.adjust import AdjustAction
from .editing_tools.style_transfer import StyleTransferAction
from .editing_tools.draw import DrawAction
from .backwards_forwards import BackwardsForwardsActions
from .hand_actuator import HandActuator
from .tool_button_style import eventFilter, build_tool_button


# pylint: disable=C0103
class EditingToolBar(QToolBar):
    """Toolbar that contains all the editing actions"""

    def __init__(self):
        super().__init__('Editing ToolBar')
        self.setMovable(False)
        self.eventFilter = eventFilter

        self.menu_tools = MenuTools(self)

        self.editing_tool_factory = EditingToolFactory(self)

        self.editing_action_container: Dict[str, EditingToolAction] = \
            {'Adjust': self.editing_tool_factory.make_editing_tool('Adjust'),
             'Resize': self.editing_tool_factory.make_editing_tool('Resize'),
             'Filter': self.editing_tool_factory.make_editing_tool('Filter'),
             'Crop': self.editing_tool_factory.make_editing_tool('Crop'),
             'Rotate': self.editing_tool_factory.make_editing_tool('Rotate'),
             'Draw': self.editing_tool_factory.make_editing_tool('Draw'),
             'Style Transfer': self.editing_tool_factory.
                 make_editing_tool('Style Transfer'),
             'Deep Dream': self.editing_tool_factory.
                 make_editing_tool('Deep Dream')}

        self.backwards_forwards_actions = BackwardsForwardsActions()

        self.setFixedHeight(100)

        self.add_actions_to_action_group()

    def new_image_setup(self):
        """Sets the view when a new image is loaded"""
        self.backwards_forwards_actions.new_image_setup()
        self.refresh()

    def refresh(self):
        """Refreshes the view"""
        self.clear()
        self.add_actions_to_action_group()

    def add_actions_to_action_group(self):
        """Adds the actions to the group"""
        left_spacer_menu_bar = QWidget()
        left_spacer_menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        left_spacer_menu_bar.setVisible(True)
        self.addWidget(left_spacer_menu_bar)

        for menu_tool_button in self.menu_tools:
            self.addWidget(menu_tool_button)

        action_group: QActionGroup = self.backwards_forwards_actions(self)
        self.addActions(action_group.actions())

        for editing_tool_action in self.editing_action_container.values():
            editing_tool_action.build_tool_button()
            self.addWidget(editing_tool_action.button)

        right_spacer_menu_bar = QWidget()
        right_spacer_menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        right_spacer_menu_bar.setVisible(True)
        self.addWidget(right_spacer_menu_bar)

    def get_hand_actuator_view(self) -> HandActuator:
        """Hand actuator view getter"""
        return self.menu_tools.hand_actuator

    def get_open_image_action(self) -> QAction:
        """Open image view getter"""
        return self.menu_tools.open_image_action

    def get_save_image_action(self) -> QAction:
        """Open image view getter"""
        return self.menu_tools.save_image_action


@dataclasses.dataclass
class EditingToolFactory:
    """Editing tool factory for the view"""
    editing_toolbar: QToolBar

    def make_editing_tool(self, action_name: str) -> Optional[EditingToolAction]:
        """Factory method"""
        editing_tool_action = None

        if action_name == 'Crop':
            editing_tool_action = CropAction(action_name, self.editing_toolbar)
        if action_name == 'Filter':
            editing_tool_action = FilterAction(action_name, self.editing_toolbar)
        if action_name == 'Resize':
            editing_tool_action = ResizeAction(action_name, self.editing_toolbar)
        if action_name == 'Rotate':
            editing_tool_action = RotateAction(action_name, self.editing_toolbar)
        if action_name == 'Draw':
            editing_tool_action = DrawAction(action_name, self.editing_toolbar)
        if action_name == 'Adjust':
            editing_tool_action = AdjustAction(action_name, self.editing_toolbar)
        if action_name == 'Style Transfer':
            editing_tool_action = StyleTransferAction(action_name, self.editing_toolbar)
        if action_name == 'Deep Dream':
            editing_tool_action = DeepDreamAction(action_name, self.editing_toolbar)
        return editing_tool_action


# pylint: disable=R0902
class MenuTools:
    """Container of the basic tools of the app"""

    def __init__(self, tool_bar: QToolBar):
        self.iterator_index = 0
        self.tool_bar = tool_bar

        self.open_image_action = QAction()
        self.open_image_button: Optional[QToolButton()] = None

        self.save_image_action = QAction()
        self.save_image_button: Optional[QToolButton()] = None

        self.hand_actuator = HandActuator(tool_bar)

        self.buttons_list: List[QToolButton] = []

    def __iter__(self):
        self.iterator_index = 0
        return self

    def __next__(self):
        if not self.iterator_index:
            self.build_buttons()
        if self.iterator_index < len(self.buttons_list):
            result = self.buttons_list[self.iterator_index]
            self.iterator_index += 1
            return result
        self.iterator_index = 0
        raise StopIteration

    def build_buttons(self):
        """Buttons builder"""
        self.open_image_button = build_tool_button(toolbar=self.tool_bar,
                                                   action=self.open_image_action,
                                                   button_text='Open',
                                                   icon_path='./resources/picture.png',
                                                   size=(0, 22))

        self.save_image_button = build_tool_button(toolbar=self.tool_bar,
                                                   action=self.save_image_action,
                                                   button_text='Save As',
                                                   icon_path='./resources/save.png',
                                                   size=(0, 20))

        self.hand_actuator.build_button()

        self.buttons_list = [self.open_image_button,
                             self.save_image_button,
                             self.hand_actuator.button]
