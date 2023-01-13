"""Hand actuator controller module"""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QDesktopWidget

from view.hand_actuator import HandActuator
from view.main_window import MainWindow
from model.hand_actuator import HandActuatorModel


class HandActuatorController:
    """Controller of the hand actuator"""
    def __init__(self, view: MainWindow, hand_actuator_view: HandActuator):
        self.view = view
        self.hand_actuator_view = hand_actuator_view
        self.hand_actuator_model = HandActuatorModel()

        self.desktop = QDesktopWidget()
        self.enabled: bool = False
        self.first_frame: bool = True

        self.connect_action_signal()
        self.hand_actuator_model.new_frame.connect(self.update_image_slot)

    def update_image_slot(self, image: QImage):
        """Function that receives a signal when a new frame comes from the webcam
        and updates the view"""
        self.hand_actuator_model.mutex.lock()
        current_frame = image.copy()
        self.hand_actuator_model.mutex.unlock()
        self.hand_actuator_view.set_pixmap(QPixmap.
                                           fromImage(current_frame).
                                           scaledToWidth(int(self.desktop.screenGeometry().
                                                             width() * 0.33)))
        if self.first_frame and self.hand_actuator_model.thread_active:
            self.hand_actuator_view.set_visible(self.hand_actuator_model.thread_active)
            self.view.central_layout.addWidget(self.hand_actuator_view.
                                               get_actuator_image(), 0, 6, 6, 3, Qt.AlignCenter)
            self.first_frame = False

    def enable_hand_actuator(self):
        """Function that starts and stops the thread that detects the hand"""
        if not self.enabled:
            self.hand_actuator_model.start()
        else:
            self.first_frame = False
            self.hand_actuator_model.stop()
            self.hand_actuator_view.set_visible(False)
            self.view.central_layout.removeWidget(self.hand_actuator_view.get_actuator_image())
            self.first_frame = True
        self.enabled = not self.enabled

    def connect_action_signal(self):
        """Connects signals with slots"""
        self.hand_actuator_view.action.triggered.connect(lambda: self.enable_hand_actuator())

    def __del__(self):
        if self.hand_actuator_model.isRunning():
            self.hand_actuator_model.stop()
