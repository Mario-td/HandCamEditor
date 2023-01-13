"""Draw view file"""
from typing import Dict, Optional

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QToolBar, QWidget, QAction, QSpinBox, QToolButton

from view.editing_tools import EditingToolAction
from view.editing_tools.editing_tool import Tool, ButtonContainer, center_widgets_in_toolbar
from ..accept_cancel import AcceptCancelContainer
from ..tool_button_style import build_tool_button


class DrawAction(EditingToolAction):
    """Drawing action view class"""
    def __init__(self, text: str, toolbar: QToolBar):
        super().__init__(text, toolbar)
        self.button_icon_path = './resources/paint_brush.png'
        self.draw_tools = DrawTools(self.toolbar)

    @center_widgets_in_toolbar
    def add_widgets_and_actions_to_toolbar(self):
        self.draw_tools.add_widgets_and_actions_to_toolbar()
        middle_spacer_menu_bar = QWidget()
        middle_spacer_menu_bar.setFixedSize(10, 30)
        middle_spacer_menu_bar.setVisible(True)
        self.toolbar.addWidget(middle_spacer_menu_bar)
        self.accept_and_cancel.add_actions_to_toolbar()


# pylint: disable=R0902
class DrawTools(Tool):
    """Tools of the draw action"""
    def __init__(self, toolbar: QToolBar):
        super().__init__(toolbar)

        self.erase = QAction()
        self.erase_button: Optional[QToolButton] = None
        self.color = QAction()
        self.color_button: Optional[QToolButton] = None
        self.effect = EffectAction(toolbar)
        self.effect_button: Optional[QToolButton] = None

        self.brush_shape_container = []
        self.brush_shape_buttons: Dict[str, QToolButton] = {}
        circle_action = QAction('Circle')
        circle_action.setIcon(QIcon(QPixmap('./resources/circle.png').scaledToHeight(22)))
        self.brush_shape_container.append(circle_action)
        rhombus_action = QAction('Rhombus')
        rhombus_action.setIcon(QIcon(QPixmap('./resources/rhombus.png')))
        self.brush_shape_container.append(rhombus_action)
        square_action = QAction('Square')
        square_action.setIcon(QIcon(QPixmap('./resources/square.png').scaledToHeight(20)))
        self.brush_shape_container.append(square_action)
        spray_action = QAction('Spray')
        spray_action.setIcon(QIcon(QPixmap('./resources/spray.png').scaled(26, 26)))
        self.brush_shape_container.append(spray_action)

        self.size_spinbox = QSpinBox()

    def add_widgets_and_actions_to_toolbar(self):
        self.build_buttons()
        self.toolbar.addWidget(self.erase_button)
        self.toolbar.addWidget(self.color_button)
        self.toolbar.addWidget(self.effect_button)
        for button in self.brush_shape_buttons.values():
            self.toolbar.addWidget(button)

        self.size_spinbox = QSpinBox()
        self.toolbar.addWidget(self.size_spinbox)

    def build_buttons(self):
        self.erase_button = build_tool_button(toolbar=self.toolbar,
                                              action=self.erase,
                                              button_text='Erase',
                                              icon_path='./resources/erase.png')
        self.color_button = build_tool_button(toolbar=self.toolbar,
                                              action=self.color,
                                              button_text='Color',
                                              icon_path='./resources/color.png')
        self.effect_button = build_tool_button(toolbar=self.toolbar,
                                               action=self.effect,
                                               button_text='Effect',
                                               icon_path='./resources/filter.png',
                                               size=(0, 30))

        for action in self.brush_shape_container:
            button = build_tool_button(toolbar=self.toolbar,
                                       action=action,
                                       button_text=action.text())
            icon: QIcon = action.icon()
            button.setIcon(icon)
            self.brush_shape_buttons[action.text()] = button


class EffectAction(QAction):
    """Effect Action, contains the filter buttons and the accept cancel widget"""
    def __init__(self, toolbar: QToolBar):
        super().__init__()
        self.toolbar = toolbar
        self.button_container = ButtonContainer(self.toolbar)

        self.cancel_effect = AcceptCancelContainer(self.toolbar)

    def display_filter_buttons(self, filtered_images):
        """Displays the filter buttons on the toolbar"""
        self.toolbar.clear()
        self.button_container.update_button_image(filtered_images)
        self.button_container.add_widgets_and_actions_to_toolbar()
        self.cancel_effect.add_actions_to_toolbar()
