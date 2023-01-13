"""Filter Action controller module"""
from PyQt5.QtWidgets import QMessageBox

from controller.utils import connect_button_to_slot
from model.editing_tools import FilterActionModel
from view.editing_tools import EditingToolAction

from .editing_tool import EditingTool, ButtonContainerController


class FilterActionController(EditingTool):
    """Controller of the filter action"""
    def __init__(self, view, model, filter_action: EditingToolAction):
        super().__init__(view, model, filter_action)
        self.filter_model: FilterActionModel = model.actions['Filter']
        self.filter_button_container_controller = \
            FilterButtonContainerController(self.view, self.model, filter_action)

        self.connect_filter_buttons_with_accept_filter_button()

    def show_tools(self):
        """Implements the abstract method"""
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to edit')
            return
        self.model.create_temp_image()
        self.filter_model.filter_container.apply_filters(self.model.tmp_img)
        self.action.button_container.update_button_image(self.filter_model.
                                           filter_container.get_filtered_images_pixmap())
        self.action.display_items()

    def connect_filter_buttons_with_accept_filter_button(self):
        """Connects the button signals"""
        [connect_button_to_slot(button,
                                self.action.accept_and_cancel.accept_action.setDisabled,
                                False)
         for button in self.action.button_container.buttons]


class FilterButtonContainerController(ButtonContainerController):
    """Contains the button filters controller"""
    def __init__(self, view, model, action):

        self.filter_model: FilterActionModel = model.actions['Filter']
        super().__init__(view, model, action)

    def connect_button_signals_to_slots(self):
        """Connects a button to a specific filter"""
        filter_temp_image = self.filter_model.filter_temp_image

        def connect(button):
            button.clicked.connect(lambda: filter_temp_image(button.toolTip()))

        [connect(button) for button in self.button_container.buttons]

    def initialize_filter_buttons(self):
        """Initial setup of the components"""
        self.button_container.populate_buttons(
            len(self.filter_model.filter_container))
