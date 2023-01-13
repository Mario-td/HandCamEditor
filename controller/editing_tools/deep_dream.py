"""Deep dream action controller module"""
from threading import Thread
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QAction, QApplication

from controller.editing_tools import EditingTool
from controller.image_viewer import ImageViewerController
from model.editing_tools import DeepDreamActionModel
from view.editing_tools import DeepDreamAction, DeepDreamTools


class DeepDreamActionController(EditingTool):
    """Controller of the style controller action"""
    def __init__(self, view, model, deep_dream_action: DeepDreamAction):
        super().__init__(view, model, deep_dream_action)
        self.deep_dream_tools_controller = DeepDreamToolsController(view,
                                                                    model,
                                                                    deep_dream_action)

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to dream about')
            return
        self.model.create_temp_image()
        self.deep_dream_tools_controller.connect_signals_to_slots()
        self.action.display_items()
        self.model.actions['Deep Dream'].resize_original_image()


class DeepDreamToolsController:
    """Controller of the deep dream tools"""
    def __init__(self, view, model, action: DeepDreamAction):
        self.view = view
        self.deep_dream_model: DeepDreamActionModel = model.actions['Deep Dream']
        self.deep_dream_view: DeepDreamAction = action
        self.deep_dream_tools: DeepDreamTools = action.deep_dream_tools
        self.connected_signals: bool = False
        self.image_viewer_controller = ImageViewerController(view, model)
        self.deep_dream_thread: Thread = Thread(target=self.deep_dream_model.apply_dream,
                                                args=('',))

    def connect_signals_to_slots(self):
        """Connects all the signals of the actions"""
        if not self.connected_signals:
            self.connect_button_signals_to_slots()
            self.deep_dream_model.signal_sender.\
                deep_dream_finished.connect(self.deep_dream_applied_slot)
            self.connected_signals = True

    def connect(self, action: QAction):
        """Connects every action for applying the deep dream"""
        action.triggered.connect(lambda: self.apply_dream(action.text()))

    def connect_button_signals_to_slots(self):
        """Method for connecting all the button signals"""
        connect = self.connect
        [connect(action) for action in self.deep_dream_tools.dreams_list]

    def apply_dream(self, dream_name: str):
        """Method that initializes the thread for applying the deep dream"""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.view.tool_bar.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.deep_dream_thread = Thread(target=self.deep_dream_model.apply_dream,
                                        args=(dream_name,))
        self.deep_dream_thread.start()

    def deep_dream_applied_slot(self):
        """Method to update the displayed image and join the thread"""
        self.image_viewer_controller.display_image()
        self.deep_dream_thread.join()
        self.view.tool_bar.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.deep_dream_view.accept_and_cancel.accept_action.setEnabled(True)
        QApplication.restoreOverrideCursor()
