"""Adjust controller file"""
from PyQt5.QtWidgets import QMessageBox

from model.editing_tools import AdjustActionModel
from model.editing_tools.adjust import SLIDER_MAX_VALUE
from view.editing_tools.adjust import AdjustAction
from .editing_tool import EditingTool
from ..image_viewer import ImageViewerController


class AdjustActionController(EditingTool):
    """Controller of the resize actions"""
    def __init__(self, view, model, adjust_action: AdjustAction):
        super().__init__(view, model, adjust_action)
        self.adjust_model: AdjustActionModel = self.model.actions['Adjust']
        self.image_viewer_controller = ImageViewerController(self.view, self.model)
        self.features_controller = AdjustFeaturesController(adjust_action,
                                                            self.adjust_model,
                                                            self.image_viewer_controller)

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to adjust')
            return
        self.model.create_temp_image()
        self.action.display_items()
        self.adjust_model.initialize_features()
        self.features_controller.configure_slider()


class AdjustFeaturesController:
    """Controller of the feature actions"""
    def __init__(self, adjust_action: AdjustAction, adjust_model: AdjustActionModel,
                 image_viewer_controller: ImageViewerController):
        self.adjust_action = adjust_action
        self.adjust_tools = self.adjust_action.adjust_tools
        self.adjust_model = adjust_model
        self.image_viewer_controller = image_viewer_controller
        self.connect_features_action_signals()

    def configure_slider(self):
        """Configures the feature changer slider"""
        self.adjust_tools.features_slider.setRange(-SLIDER_MAX_VALUE, SLIDER_MAX_VALUE)
        self.adjust_tools.features_slider.setEnabled(False)
        self.adjust_tools.features_slider.valueChanged.connect(self.slider_value_changed)

    def connect_features_action_signals(self):
        """Connects the action signals to emit the action name"""
        emit_feature_name = self.emit_feature_name

        def connect(action):
            action.triggered.connect(lambda: emit_feature_name(action.text()))

        [connect(action) for action in self.adjust_tools.adjustable_features]

    def emit_feature_name(self, feature_name):
        """Emits the action name"""
        self.adjust_model.set_feature(feature_name)
        self.adjust_tools.features_slider.setEnabled(True)
        self.adjust_tools.features_slider.setValue(self.adjust_model.get_feature_value())

    def slider_value_changed(self, value: int):
        """Changes the value of the slider"""
        self.adjust_action.accept_and_cancel.accept_action.setEnabled(True)
        self.adjust_model.change_value(value)
        self.image_viewer_controller.display_image()
