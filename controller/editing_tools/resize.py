"""Resize action controller module"""
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject

from controller.image_viewer import ImageViewerController
from view.editing_tools import EditingToolAction
from view.editing_tools.resize import MAX_HEIGHT, MAX_WIDTH

from .editing_tool import EditingTool


class ResizeActionController(EditingTool):
    """Controller of the resize actions"""
    def __init__(self, view, model, resize_action: EditingToolAction):
        super().__init__(view, model, resize_action)

        self.resize_tools_controller = ResizeToolsController(view, model)

        self.connect_signals_between_elements()

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to resize')
            return
        self.model.create_temp_image()
        self.action.display_items()
        self.resize_tools_controller.display_image_size()
        self.action.resize_tools.aspect_ratio_checkbox.setChecked(True)
        self.resize_tools_controller.set_slider_value()

    def enable_accept_action(self, value):
        """Receives a signal to enable the accept action"""
        self.accept_action.setDisabled(value)

    def connect_signals_between_elements(self):
        """Connects the size changed signal of the controller"""
        self.resize_tools_controller.size_changed.connect(self.enable_accept_action)


class ResizeToolsController(QObject):
    """Controller of the resize tools"""
    def __init__(self, view, model):
        super().__init__()
        self.image_viewer_controller = ImageViewerController(view, model)
        self.view = view
        self.model = model
        self.resize_tools = self.view.tool_bar.editing_action_container['Resize'].resize_tools

        self.connect_signals()

        self.new_width = 1
        self.new_height = 1

    size_changed = pyqtSignal(bool)

    def set_slider_value(self):
        """Slider value setter"""
        self.resize_tools.size_slider.setValue(self.model.get_current_image_size()[1])

    def new_image(self):
        """Actions carried out when a new image is loaded"""
        self.image_viewer_controller.display_image(self.model.get_temp_pixmap)

        if (self.new_height, self.new_width) == self.model.get_current_image_size():
            self.size_changed.emit(True)
        else:
            self.size_changed.emit(False)

    def change_width(self):
        """Changes the width of the image"""
        self.new_width = int('0' + ''.join(c for c
                                           in self.resize_tools.width_line_edit.text()
                                           if c.isdigit()))
        if not self.new_width:
            self.new_width = 1

        if self.resize_tools.aspect_ratio_checkbox.isChecked():
            _, self.new_height = self.model.actions['Resize'].\
                get_size_with_ratio(width=self.new_width)
            if not self.new_height:
                self.new_height = 1
            elif self.new_height > MAX_HEIGHT:
                self.new_height = MAX_HEIGHT
                self.resize_tools.aspect_ratio_checkbox.setChecked(False)
            self.model.actions['Resize'].change_temp_image_height(self.new_height)
            self.resize_tools.height_line_edit.blockSignals(True)
            self.resize_tools.height_line_edit.setText(str(self.new_height))
            self.resize_tools.height_line_edit.blockSignals(False)

        self.model.actions['Resize'].change_temp_image_width(self.new_width)
        self.new_image()

    def change_height(self):
        """Changes the height of the image"""
        self.new_height = int('0' + ''.join(c for c
                                            in self.resize_tools.height_line_edit.text()
                                            if c.isdigit()))
        if not self.new_height:
            self.new_height = 1

        if self.resize_tools.aspect_ratio_checkbox.isChecked():
            self.new_width, _ = self.model.actions['Resize']\
                .get_size_with_ratio(height=self.new_height)
            if not self.new_width:
                self.new_width = 1
            elif self.new_width > MAX_WIDTH:
                self.new_width = MAX_WIDTH
                self.resize_tools.aspect_ratio_checkbox.setChecked(False)
            self.model.actions['Resize'].change_temp_image_width(self.new_width)
            self.resize_tools.width_line_edit.blockSignals(True)
            self.resize_tools.width_line_edit.setText(str(self.new_width))
            self.resize_tools.width_line_edit.blockSignals(False)

        self.model.actions['Resize'].change_temp_image_height(self.new_height)
        self.new_image()

    def display_image_size(self):
        """Shows the image size in the text elements"""
        image_size = self.model.get_current_image_size()
        self.resize_tools.width_line_edit.setText(str(image_size[1]))
        self.resize_tools.height_line_edit.setText(str(image_size[0]))

    def slider_value_changed(self):
        """Actions carried out when the slider value changes"""
        self.resize_tools.aspect_ratio_checkbox.setChecked(True)
        self.resize_tools.width_line_edit.setText(str(self.resize_tools.size_slider.value()))

    def connect_signals(self):
        """Connects the signals of the resize elements"""
        self.resize_tools.width_line_edit.textChanged.connect(self.change_width)
        self.resize_tools.height_line_edit.textChanged.connect(self.change_height)
        self.resize_tools.size_slider.valueChanged.connect(self.slider_value_changed)
