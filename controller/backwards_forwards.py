"""Backward and forward controller module"""
from .image_viewer import ImageViewerController


class BackwardsForwardsActionsController:
    """Controller of the element that contains the backward and forward actions"""
    def __init__(self, view, model, backwards_forwards_actions):
        self.image_viewer_controller = ImageViewerController(view, model)
        self.backwards_forwards_action = backwards_forwards_actions
        self.model = model

        self.connect_action_signals()

    def redo_undo_image(self, redo: bool):
        """Updates the elements depending on do or undo actions"""
        if redo:
            self.model.redo_image()
        else:
            self.model.undo_image()
        self.update_state()
        self.image_viewer_controller.display_image(self.model.get_current_pixmap)

    def update_state(self):
        """Updates the view depending on the state"""
        if self.model.idx_current_img == 0:
            if len(self.model.history_img) < 2:
                self.backwards_forwards_action.update_state_view('')
            else:
                self.backwards_forwards_action.update_state_view('r')
        elif self.model.idx_current_img == len(self.model.history_img) - 1:
            self.backwards_forwards_action.update_state_view('l')
        else:
            self.backwards_forwards_action.update_state_view('b')

    def connect_action_signals(self):
        """Connects the actions with the signals"""
        self.backwards_forwards_action.backwards_action.triggered.\
            connect(lambda: self.redo_undo_image(False))
        self.backwards_forwards_action.forwards_action.triggered.\
            connect(lambda: self.redo_undo_image(True))
