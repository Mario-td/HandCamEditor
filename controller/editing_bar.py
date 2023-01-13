"""Editing toolbar controller module"""
from typing import Optional

from PyQt5.QtWidgets import QAction

from view.editing_bar import EditingToolBar
from view.editing_tools import FilterAction, CropAction, \
    ResizeAction, RotateAction, AdjustAction, DrawAction, StyleTransferAction, \
    DeepDreamAction
from .backwards_forwards import BackwardsForwardsActionsController
from .editing_tools import FilterActionController, ResizeActionController, \
    CropActionController, EditingTool, RotateActionController, AdjustActionController,\
    StyleTransferActionController, DeepDreamActionController
from .editing_tools.draw import DrawActionController


class EditingToolBarController:
    """Controller of the editing toolbar"""
    def __init__(self, view, model, tool_bar: EditingToolBar):
        self.tool_bar = tool_bar

        self.backwards_forwards_actions_controller =\
            BackwardsForwardsActionsController(view, model,
                                               tool_bar.backwards_forwards_actions)

        self.action_controller_factory = EditingToolControllerFactory()

        self.action_list = []

        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Filter']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Crop']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Rotate']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Resize']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Draw']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Adjust']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.
                                                  editing_action_container['Style Transfer']))
        self.action_list.append(self.action_controller_factory.
                                make_editing_tool(view, model,
                                                  tool_bar.editing_action_container['Deep Dream']))
        self.connect_signals_between_components()

    def connect_signals_between_components(self):
        """Connects the signals with the backwards forwards component"""
        for action in self.action_list:
            action.accept_cancel_controller.image_viewer_controller.image_changed.\
                connect(lambda: self.backwards_forwards_actions_controller.update_state())


class EditingToolControllerFactory:
    """Factory class of the editing tools"""

    @staticmethod
    def make_editing_tool(view, model, action: QAction) -> Optional[EditingTool]:
        """Factory method"""
        editing_tool = None
        if isinstance(action, FilterAction):
            editing_tool = FilterActionController(view, model, action)
        if isinstance(action, CropAction):
            editing_tool = CropActionController(view, model, action)
        if isinstance(action, ResizeAction):
            editing_tool = ResizeActionController(view, model, action)
        if isinstance(action, RotateAction):
            editing_tool = RotateActionController(view, model, action)
        if isinstance(action, DrawAction):
            editing_tool = DrawActionController(view, model, action)
        if isinstance(action, AdjustAction):
            editing_tool = AdjustActionController(view, model, action)
        if isinstance(action, StyleTransferAction):
            editing_tool = StyleTransferActionController(view, model, action)
        if isinstance(action, DeepDreamAction):
            editing_tool = DeepDreamActionController(view, model, action)
        return editing_tool
