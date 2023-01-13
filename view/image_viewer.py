"""Image viewer view module"""
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QFrame, QGraphicsPixmapItem
from PyQt5.QtCore import QRectF, QMarginsF, QObject, pyqtSignal, QEvent, QPointF


class ImageViewer:
    """View of the displayed image"""
    def __init__(self):
        self.image_scene = QGraphicsScene()
        self.image_view = QGraphicsView(self.image_scene)
        self.image_view.setFrameStyle(QFrame.NoFrame)

        self.graphics_pixmap = QGraphicsPixmapItem()
        self.graphics_pixmap.setAcceptHoverEvents(True)
        self.image_scene.addItem(self.graphics_pixmap)

        self.signal_sender = SignalSender()

        self.assign_events()

    def display_image(self, image):
        """Displays the editing image"""
        self.graphics_pixmap.setPixmap(image)
        self.image_scene.setSceneRect(QRectF(image.rect()).marginsAdded(QMarginsF(1, 1, 1, 1)))

    def assign_events(self):
        """Assigns signals to the events"""
        self.graphics_pixmap.hoverEnterEvent = self.signal_sender.enter_into_image
        self.graphics_pixmap.hoverLeaveEvent = self.signal_sender.leave_image
        self.graphics_pixmap.hoverMoveEvent = self.signal_sender.image_coordinate
        self.graphics_pixmap.mousePressEvent = self.signal_sender.pressed_image


class SignalSender(QObject):
    """Contains all the signals that are emitted when
    the events are triggered on the image viewer"""

    enter_image_signal = pyqtSignal(QPointF)
    leave_image_signal = pyqtSignal()
    image_coordinate_signal = pyqtSignal(QPointF)
    mouse_pressed_image_signal = pyqtSignal()
    mouse_pressed_image_signal_coordinate = pyqtSignal(QPointF)

    def enter_into_image(self, event: QEvent):
        """Triggers the enter image signal"""
        self.enter_image_signal.emit(event.pos())

    def leave_image(self, _):
        """Triggers the leave image signal"""
        self.leave_image_signal.emit()

    def image_coordinate(self, event: QEvent):
        """Emits the coordinates of the image when it is hovered"""
        self.image_coordinate_signal.emit(event.pos())

    def pressed_image(self, event: QEvent):
        """Emits the coordinates of the image where it is pressed"""
        self.mouse_pressed_image_signal.emit()
        self.mouse_pressed_image_signal_coordinate.emit(event.pos())
