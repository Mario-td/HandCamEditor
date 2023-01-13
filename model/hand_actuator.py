"""View of the webcam hand actuator"""
from typing import Optional

import numpy as np
import cv2
import mediapipe as mp
from PyQt5.QtWidgets import QDesktopWidget
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QThread, QMutex, pyqtSignal

from pynput.mouse import Controller, Button

PRESS = 1
HOVER = 2
DOUBLE_CLICK = 3

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


class HandActuatorModel(QThread):
    """Thread for capturing frames from the webcam"""

    def __init__(self):
        super().__init__()
        self.thread_active = False
        self.mutex = QMutex()
        self.hand = HandActuator()
        self.cap: Optional[cv2.VideoCapture] = None

    new_frame = pyqtSignal(QImage)

    def run(self):
        """Starting point of the thread"""
        self.thread_active = True
        self.cap: cv2.VideoCapture = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        while self.thread_active:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame.flags.writeable = False
                self.hand.detect_action(frame, draw_circle=True, draw_skeleton=True)
                frame = cv2.flip(frame, 1)
                self.mutex.lock()
                frame_qt_format = QImage(frame.data, frame.shape[1],
                                         frame.shape[0], QImage.Format_RGB888)
                self.new_frame.emit(frame_qt_format)
                self.mutex.unlock()
                self.hand.handle_action()

    def stop(self):
        """Finishing point of the thread"""
        self.thread_active = False
        self.cap.release()
        self.quit()
        self.wait()


class HandActuator:
    """Detects the hand landmarks and determines what action is performed."""

    def __init__(self):
        self.hand_detector = Detector(min_detection_confidence=0.8,
                                      min_tracking_confidence=0.4)

        self.action_rectangle = ActionRectangle()

        self.mouse_mover = MouseMover(rect_action=self.action_rectangle)

        self.previous_action = None
        self.action = None
        self.index_tip_x = 0
        self.index_tip_y = 0

    def detect_action(self, frame, draw_circle=True, draw_skeleton=True, draw_rectangle=True):
        """Sets which action is performed depending on the fingers position"""
        if self.hand_detector.detect_landmarks(frame):
            self.previous_action = self.action
            if self.is_index_raised():
                if self.is_thumb_closed():
                    self.action = PRESS
                else:
                    self.action = HOVER
                self.index_tip_x = self.hand_detector.landmarks[8].x
                self.index_tip_y = self.hand_detector.landmarks[8].y
            else:
                self.action = None
            frame.flags.writeable = True
            if draw_circle:
                self.hand_detector.draw_action_circle(frame, self.action,
                                                      self.index_tip_x, self.index_tip_y)
            if draw_skeleton:
                self.hand_detector.draw_hand_skeleton(frame)
        else:
            self.action = None
        if draw_rectangle:
            cv2.rectangle(frame, (self.action_rectangle.origin_x, self.action_rectangle.origin_y),
                          (self.action_rectangle.origin_x + self.action_rectangle.width,
                           self.action_rectangle.origin_y + self.action_rectangle.height),
                          (0, 0, 0), 2)

    def is_thumb_closed(self) -> bool:
        """Checks if the thumb is bent"""
        if self.hand_detector.results.multi_handedness[0].classification[0].label == 'Left':
            return self.hand_detector.landmarks[4].x < self.hand_detector.landmarks[3].x
        return self.hand_detector.landmarks[4].x > self.hand_detector.landmarks[3].x

    def is_index_raised(self) -> bool:
        """Checks if index finger is raised"""
        return self.hand_detector.landmarks[8].y < self.hand_detector.landmarks[5].y

    def action_changed(self) -> bool:
        """Stores the previous action"""
        return self.previous_action != self.action

    def handle_action(self):
        """Performs an action on the mouse depending of the detected result"""
        if self.action_changed():
            if self.action == HOVER:
                self.mouse_mover.mouse.release(Button.left)
            elif self.action == PRESS:
                self.mouse_mover.mouse.press(Button.left)
            elif self.action == DOUBLE_CLICK:
                self.mouse_mover.mouse.release(Button.left)
                self.mouse_mover.mouse.click(Button.left, 2)
            else:
                self.mouse_mover.mouse.release(Button.left)
        self.mouse_mover.move(self.action, self.index_tip_x, self.index_tip_y)


class ActionRectangle:
    """Rectangle where the hand is detected"""
    def __init__(self):
        self.origin_x: int = int(FRAME_WIDTH * 0.15)
        self.origin_y: int = int(FRAME_HEIGHT * 0.02)
        self.width: int = FRAME_WIDTH - 2 * self.origin_x
        self.height: int = FRAME_HEIGHT - self.origin_y - int(self.width * 0.45)

    def get_height(self):
        """Height getter"""
        return self.height

    def get_origin_x(self):
        """Origin x getter"""
        return self.origin_x

    def get_origin_y(self):
        """Origin y getter"""
        return self.origin_y


class Detector(mp.solutions.hands.Hands):
    """Hand detector"""
    def __init__(self,
                 static_image_mode=False,
                 max_num_hands=1,
                 min_detection_confidence=0.5,
                 min_tracking_confidence=0.5):
        super().__init__(static_image_mode, max_num_hands,
                         min_detection_confidence, min_tracking_confidence)

        self.landmarks = None
        self.results = None

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_hands = mp.solutions.hands

    def detect_landmarks(self, img) -> bool:
        """Detects hand landmarks given an image"""
        self.results = self.process(img)
        if self.results.multi_hand_landmarks:
            self.landmarks = self.results.multi_hand_landmarks[0].landmark
            return True
        self.landmarks = None
        return False

    @staticmethod
    def draw_action_circle(frame, action, index_tip_x, index_tip_y):
        """Draws a circle on the frame where the action is detected"""
        if action:
            if action == PRESS:
                color = (0, 0, 255)
            elif action == DOUBLE_CLICK:
                color = (255, 0, 0)
            else:
                color = (0, 255, 0)
            cv2.circle(frame, (int(index_tip_x * frame.shape[1]),
                               int(index_tip_y * frame.shape[0])),
                       50, color, cv2.FILLED)

    def draw_hand_skeleton(self, frame):
        """Draws the hand skeleton"""
        for hand_landmarks in self.results.multi_hand_landmarks:
            self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)


class MouseMover:
    """Handles the mouse moves"""
    def __init__(self, rect_action: ActionRectangle):
        self.mouse = Controller()

        self.desktop = QDesktopWidget()

        self.pos_x = self.desktop.width() / 2
        self.pos_y = self.desktop.height() / 2

        self.mouse_filter = MouseFilter(self.desktop, rect_action)

    def move(self, action, pos_x: float, pos_y: float):
        """Moves the mouse to the specified coordinates"""
        if action:
            self.filter_position(pos_x, pos_y)
            self.mouse.position = (int(self.interpolate_x((self.desktop.width() - self.pos_x))),
                                   int(self.interpolate_y(self.pos_y)))

    def interpolate_x(self, position_x):
        """Performs the interpolation in the x coordinate"""
        return np.interp(position_x,
                         (self.mouse_filter.get_offset_x(),
                          self.desktop.width() - self.mouse_filter.get_offset_x()),
                         (0, self.desktop.width()))

    def interpolate_y(self, position_y):
        """Performs the interpolation in the y coordinate"""
        return np.interp(position_y,
                         (self.mouse_filter.get_offset_y_above(),
                          self.desktop.height() - self.mouse_filter.get_offset_y_bellow()),
                         (0, self.desktop.height()))

    def filter_position(self, pos_x, pos_y):
        """Filters the position"""
        pos_x *= self.desktop.width()
        pos_y *= self.desktop.height()
        self.pos_x = self.pos_x + (pos_x - self.pos_x) / self.mouse_filter.filter_factor
        self.pos_y = self.pos_y + (pos_y - self.pos_y) / self.mouse_filter.filter_factor


def moved_distance(new_pos_x, new_pos_y, old_pos_x, old_pos_y):
    """Calculates the moved distance, the Chebyshev distance"""
    return max(abs(new_pos_x - old_pos_x), abs(new_pos_y - old_pos_y))


class MouseFilter:
    """Filters the mouse position to avoid noise in its movement"""
    def __init__(self, desktop: QDesktopWidget, rectangle: ActionRectangle):
        self.desktop = desktop
        self.rect_action = rectangle

        self.filter_factor = 4
        self.distance_to_filter = 10

        self.offset_x = self.desktop.width() * self.rect_action.get_origin_x() / FRAME_WIDTH
        self.offset_y_above = self.desktop.height() * \
            self.rect_action.get_origin_y() / FRAME_HEIGHT
        self.offset_y_bellow = self.desktop.height() * \
            (FRAME_HEIGHT - (self.rect_action.height + self.rect_action.get_origin_y()))\
            / FRAME_HEIGHT

    def get_offset_x(self):
        """X offset getter"""
        return self.offset_x

    def get_offset_y_above(self):
        """Y above offset getter"""
        return self.offset_y_above

    def get_offset_y_bellow(self):
        """Y bellow offset getter"""
        return self.offset_y_bellow

    def filter_position(self, new_pos_x, new_pos_y, old_pos_x, old_pos_y):
        """Filters the position"""
        filter_factor = 6
        if moved_distance(new_pos_x, new_pos_y, old_pos_x, old_pos_y) < \
                self.distance_to_filter:
            filter_factor = self.filter_factor

        return old_pos_x + (new_pos_x - old_pos_x) / filter_factor, \
            old_pos_y + (new_pos_y - old_pos_y) / filter_factor
