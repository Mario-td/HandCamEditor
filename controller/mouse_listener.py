"""Mouse listener file"""
from abc import abstractmethod

from PyQt5.QtCore import QObject, QPointF
from pynput.mouse import Listener


class MouseListener(QObject):
    """Listens to the mouse events to update the image"""
    def __init__(self):
        super().__init__()
        self.pressed = False
        self.listener = None
        self.initial_pos: list = [0, 0]
        self.on_pixmap = False
        self.moved_dist: list = [0, 0]
        self.initial_pressed_coordinate = QPointF()

    def construct_listener(self):
        """Listener constructor"""
        self.listener = Listener(
            on_move=self.on_move,
            on_click=self.on_click)
        self.listener.start()

    def destroy_listener(self):
        """Listener destructor"""
        self.listener.stop()
        del self.listener
        self.listener = None

    @abstractmethod
    def on_move(self, pos_x, pos_y):
        """On move event listener"""

    @abstractmethod
    def on_click(self, pos_x, pos_y, _, pressed):
        """On click event listener"""
