"""Accept and cancel controller module"""
from PyQt5.QtWidgets import QAction
from .image_viewer import ImageViewerController


class AcceptCancelController:
    """Controller of the element that accepts or cancels the edited picture"""
    def __init__(self, view, model, accept_action: QAction, cancel_action: QAction):
        self.image_viewer_controller = ImageViewerController(view, model)
        self.view = view
        self.model = model
        self.accept_action = accept_action
        self.cancel_action = cancel_action

        self.connect_accept_and_cancel_actions()

    def accept_and_update_image(self):
        """Inserts the image and updates the element that displays it"""
        self.model.insert_new_image()
        self.image_viewer_controller.display_image(self.model.get_current_pixmap)

    def cancel_and_update_image(self):
        """Simply displays the current image and not the temporary"""
        self.image_viewer_controller.display_image(self.model.get_current_pixmap)

    def connect_accept_and_cancel_actions(self):
        """Connects the accept and cancel actions"""
        self.cancel_action.triggered.connect(self.view.restored_ui_setup)
        self.cancel_action.triggered \
            .connect(self.cancel_and_update_image)

        self.accept_action.triggered.connect(self.view.restored_ui_setup)
        self.accept_action.triggered \
            .connect(self.accept_and_update_image)
