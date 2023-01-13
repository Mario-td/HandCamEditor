"""Editing tool controller module"""
from abc import ABC, abstractmethod

from controller.accept_cancel import AcceptCancelController
from controller.image_viewer import ImageViewerController
from controller.utils import connect_button_to_slot
from view.editing_tools import EditingToolAction


class EditingTool(ABC):
    """Editing tool abstract class"""
    def __init__(self, view, model, action: EditingToolAction):
        self.initialized = False

        self.view = view
        self.model = model
        self.action = action

        self.accept_action = self.action.accept_and_cancel.get_accept_action()
        self.cancel_action = self.action.accept_and_cancel.get_cancel_action()

        self.accept_cancel_controller = \
            AcceptCancelController(view, model, self.accept_action, self.cancel_action)

        if not self.initialized:
            self.initialized = True
            self()

    def __call__(self):
        self.connect_action_signal()

    @abstractmethod
    def show_tools(self):
        """Places the tools on the bar"""

    def connect_action_signal(self):
        """The action to the function that displays the editing elements"""
        self.action.triggered.connect(lambda: self.show_tools())


class ButtonContainerController:
    """Contains the button filters controller"""
    def __init__(self, view, model, action):

        self.image_viewer_controller = ImageViewerController(view, model)
        self.view = view
        self.model = model
        self.button_container = \
            action.button_container

        self.initialize_filter_buttons()
        self.connect_filter_tool_signals()
        self.connect_button_to_slot()

    @abstractmethod
    def connect_button_signals_to_slots(self):
        """Connects the button signals to their slots"""

    def connect_left_and_right_action_signals(self):
        """Connects the left and right action for moving the scroll area"""
        self.button_container.move_scroll_area_left_action.triggered.connect(
            lambda: self.button_container.scrollbar.setValue(
                self.button_container.scrollbar.value() - 40))
        self.button_container.move_scroll_area_right_action.triggered.connect(
            lambda: self.button_container.scrollbar.setValue(
                self.button_container.scrollbar.value() + 40))

    def connect_filter_tool_signals(self):
        """Method that connects all the components"""
        self.connect_left_and_right_action_signals()
        self.connect_button_signals_to_slots()

    @abstractmethod
    def initialize_filter_buttons(self):
        """Initial setup of the components"""

    def connect_button_to_slot(self):
        """Method for connecting the button signals"""
        [connect_button_to_slot(button,
                                self.image_viewer_controller.display_image,
                                self.model.get_temp_pixmap)
         for button in self.button_container.buttons]
