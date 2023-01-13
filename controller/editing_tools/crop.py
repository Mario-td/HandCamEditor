"""Crop controller file"""
import enum

from PyQt5.QtCore import Qt, pyqtSlot, QPointF, QObject, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QMessageBox
from view.editing_tools import EditingToolAction
from view.editing_tools.crop import MIN_HEIGHT, MIN_WIDTH, CropTools

from controller.mouse_listener import MouseListener
from .editing_tool import EditingTool


class CropActionController(EditingTool):
    """Controller of the cropping action"""
    def __init__(self, view, model, crop_action: EditingToolAction):
        super().__init__(view, model, crop_action)
        self.image_viewer = view.image_viewer
        self.crop_model = self.model.actions['Crop']
        self.rectangle = Rectangle(view, model)
        self.mouse = CropMouseListener(self.rectangle)
        self.pixmap = QPixmap()
        self.signal_receiver = SignalReceiver(self, self.rectangle)
        self.crop_tools_controller = CropToolsController(crop_action.crop_tools,
                                                         self.rectangle, model)
        self.connect_signals()

    def set_initial_rectangle(self):
        """Initial rectangle setter"""
        img_height, img_width = self.model.get_current_image_size()
        self.rectangle.set_origin_x(0)
        self.rectangle.set_origin_y(0)
        self.rectangle.set_width(img_width)
        self.rectangle.set_height(img_height)

        self.pixmap = self.model.get_current_pixmap()
        self.rectangle.painter.set_pixmap(self.pixmap)
        self.rectangle.painter.draw()

    def enable_accept_action(self, value):
        """Receives a signal to enable the accept action"""
        self.accept_action.setDisabled(not value)

    def crop_image(self):
        """Crops the image using the model"""
        self.crop_model.crop_image(self.rectangle.origin[0], self.rectangle.origin[1],
                                   self.rectangle.size[0], self.rectangle.size[1])
        self.accept_cancel_controller.accept_and_update_image()

    def connect_signals_between_elements(self, activate: bool):
        """"Method for connecting signals between components"""
        if activate:
            self.image_viewer.signal_sender. \
                enter_image_signal.connect(self.signal_receiver.mouse_entered_the_pixmap)
            self.image_viewer.signal_sender.\
                image_coordinate_signal.connect(self.signal_receiver.change_cursor_shape)
            self.image_viewer.signal_sender.\
                leave_image_signal.connect(self.signal_receiver.mouse_out_of_pixmap)
            self.image_viewer.signal_sender.\
                mouse_pressed_image_signal.connect(self.signal_receiver.image_pressed)
            self.mouse.pressed_moving_signal.connect(self.signal_receiver.change_rect)
            self.mouse.construct_listener()
            self.crop_tools_controller.rectangle_changed_signal.connect(self.enable_accept_action)
        else:
            self.image_viewer.signal_sender. \
                enter_image_signal.disconnect(self.signal_receiver.mouse_entered_the_pixmap)
            self.image_viewer.signal_sender.image_coordinate_signal.\
                disconnect(self.signal_receiver.change_cursor_shape)
            self.image_viewer.signal_sender.\
                leave_image_signal.disconnect(self.signal_receiver.mouse_out_of_pixmap)
            self.image_viewer.signal_sender.mouse_pressed_image_signal.\
                disconnect(self.signal_receiver.image_pressed)
            self.mouse.pressed_moving_signal.disconnect(self.signal_receiver.change_rect)
            self.mouse.destroy_listener()
            self.image_viewer.image_view.viewport().setCursor(Qt.ArrowCursor)
            self.crop_tools_controller.rectangle_changed_signal.\
                disconnect(self.enable_accept_action)

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to crop')
            return
        self.model.create_temp_image()
        self.action.display_items()
        self.accept_action.setEnabled(False)
        self.connect_signals_between_elements(True)
        self.set_initial_rectangle()
        self.rectangle.painter.draw()
        self.image_viewer.graphics_pixmap.setPixmap(self.pixmap)
        self.crop_tools_controller.display_rect_shape_param()

    def connect_signals(self):
        """Method for connecting signals"""
        self.cancel_action.triggered.connect(self.connect_signals_between_elements, False)
        self.accept_action.triggered.connect(self.connect_signals_between_elements, False)
        self.accept_action.triggered.connect(lambda: self.crop_image())
        self.accept_action.triggered.\
            disconnect(self.accept_cancel_controller.accept_and_update_image)


class Rectangle:
    """Class for shaping and displaying the rectangle"""
    def __init__(self, view, model):
        self.origin: list = [0, 0]
        self.size: list = [0, 0]

        self.get_current_pixmap = model.get_current_pixmap
        self.image_viewer = view.image_viewer

        self.hovered_part = RectanglePart.NONE

        self.painter = RectanglePainter(self)
        self.shape_changer = RectangleShapeChanger(self)

    def set_origin_x(self, origin_x: int):
        """X origin setter"""
        self.origin[0] = origin_x

    def set_origin_y(self, origin_y: int):
        """Y origin setter"""
        self.origin[1] = origin_y

    def set_width(self, width: int):
        """Width setter"""
        self.size[0] = width

    def set_height(self, height: int):
        """Height setter"""
        self.size[1] = height

    def display_rect(self):
        """Displays the rectangle on the image viewer"""
        pixmap = self.get_current_pixmap()
        self.painter.set_pixmap(pixmap)
        self.painter.draw()
        self.image_viewer.graphics_pixmap.setPixmap(pixmap)


class CropToolsController(QObject):
    """Controller of the crop tools"""
    def __init__(self, crop_tools: CropTools, rectangle: Rectangle, model):
        super().__init__()
        self.crop_tools = crop_tools
        self.rectangle = rectangle

        self.get_image_size = model.get_current_image_size

        self.connect_signals()

        self.rectangle.shape_changer.width_changed_signal.connect(self.change_width_text)
        self.rectangle.shape_changer.height_changed_signal.connect(self.change_height_text)
        self.rectangle.shape_changer.origin_x_changed_signal.connect(self.change_origin_x_text)
        self.rectangle.shape_changer.origin_y_changed_signal.connect(self.change_origin_y_text)

    rectangle_changed_signal = pyqtSignal(bool)

    def rect_changed(self):
        """Emits a signal whether the shape changed or not"""
        if (self.rectangle.size[1], self.rectangle.size[0]) != self.get_image_size():
            self.rectangle_changed_signal.emit(True)
        else:
            self.rectangle_changed_signal.emit(False)

    @pyqtSlot()
    def change_height_text(self):
        """Updates the height edit line"""
        self.crop_tools.height_line_edit.blockSignals(True)
        self.crop_tools.height_line_edit.setText(str(self.rectangle.size[1]))
        self.crop_tools.height_line_edit.blockSignals(False)
        self.rect_changed()

    @pyqtSlot()
    def change_width_text(self):
        """Updates the width edit line"""
        self.crop_tools.width_line_edit.blockSignals(True)
        self.crop_tools.width_line_edit.setText(str(self.rectangle.size[0]))
        self.crop_tools.width_line_edit.blockSignals(False)
        self.rect_changed()

    @pyqtSlot()
    def change_origin_x_text(self):
        """Updates the origin x edit line"""
        self.crop_tools.x_offset_line_edit.blockSignals(True)
        if self.rectangle.origin[0] < 0:
            self.crop_tools.x_offset_line_edit.setText('0')
        else:
            self.crop_tools.x_offset_line_edit.setText(str(self.rectangle.origin[0]))
        self.crop_tools.x_offset_line_edit.blockSignals(False)
        self.rect_changed()

    @pyqtSlot()
    def change_origin_y_text(self):
        """Updates the origin y edit line"""
        self.crop_tools.y_offset_line_edit.blockSignals(True)
        if self.rectangle.origin[1] < 0:
            self.crop_tools.y_offset_line_edit.setText('0')
        else:
            self.crop_tools.y_offset_line_edit.setText(str(self.rectangle.origin[1]))
        self.crop_tools.y_offset_line_edit.blockSignals(False)
        self.rect_changed()

    def display_rect_shape_param(self):
        """Displays the rect parameters in the edit lines"""
        self.disconnect_signals()
        self.crop_tools.width_line_edit.setText(str(self.rectangle.size[0]))
        self.crop_tools.height_line_edit.setText(str(self.rectangle.size[1]))
        self.crop_tools.x_offset_line_edit.setText(str(self.rectangle.origin[0]))
        self.crop_tools.y_offset_line_edit.setText(str(self.rectangle.origin[1]))
        self.connect_signals()

    def change_rect_width(self):
        """Changes the width from the edit line"""
        width = int('0' + ''.join(c for c
                                  in self.crop_tools.width_line_edit.text()
                                  if c.isdigit()))
        if width < MIN_WIDTH:
            width = MIN_WIDTH
        elif width + self.rectangle.origin[0] > self.get_image_size()[1]:
            width = self.get_image_size()[1] - self.rectangle.origin[0]

        self.rectangle.set_width(width)
        self.change_width_text()
        self.rectangle.display_rect()

    def change_rect_height(self):
        """Changes the height from the edit line"""
        height = int('0' + ''.join(c for c
                                   in self.crop_tools.height_line_edit.text()
                                   if c.isdigit()))
        if height < MIN_HEIGHT:
            height = MIN_HEIGHT
        elif height + self.rectangle.origin[1] > self.get_image_size()[0]:
            height = self.get_image_size()[0] - self.rectangle.origin[1]

        self.rectangle.set_height(height)
        self.change_height_text()
        self.rectangle.display_rect()

    def change_rect_origin_x(self):
        """Changes the origin x from the edit line"""
        origin_x = int('0' + ''.join(c for c
                                     in self.crop_tools.x_offset_line_edit.text()
                                     if c.isdigit()))
        if origin_x < 0:
            origin_x = 0
        elif origin_x + self.rectangle.size[0] > self.get_image_size()[1]:
            width = self.get_image_size()[1] - origin_x
            if width < MIN_WIDTH:
                width = MIN_WIDTH
                origin_x = self.get_image_size()[1] - MIN_WIDTH
            self.rectangle.set_width(width)
            self.change_width_text()

        self.rectangle.set_origin_x(origin_x)
        self.change_origin_x_text()
        self.rectangle.display_rect()

    def change_rect_origin_y(self):
        """Changes the origin y from the edit line"""
        origin_y = int('0' + ''.join(c for c
                                     in self.crop_tools.y_offset_line_edit.text()
                                     if c.isdigit()))
        if origin_y < 0:
            origin_y = 0
        elif origin_y + self.rectangle.size[1] > self.get_image_size()[0]:
            height = self.get_image_size()[0] - origin_y
            if height < MIN_HEIGHT:
                height = MIN_HEIGHT
                origin_y = self.get_image_size()[0] - MIN_HEIGHT
            self.rectangle.set_height(height)
            self.change_height_text()

        self.rectangle.set_origin_y(origin_y)
        self.change_origin_y_text()
        self.rectangle.display_rect()

    def connect_signals(self):
        """Connects the signals of the crop elements"""
        self.crop_tools.width_line_edit.textChanged.connect(self.change_rect_width)
        self.crop_tools.height_line_edit.textChanged.connect(self.change_rect_height)
        self.crop_tools.x_offset_line_edit.textChanged.connect(self.change_rect_origin_x)
        self.crop_tools.y_offset_line_edit.textChanged.connect(self.change_rect_origin_y)

    def disconnect_signals(self):
        """Disconnects the signals of the crop elements"""
        self.crop_tools.width_line_edit.textChanged.disconnect(self.change_rect_width)
        self.crop_tools.height_line_edit.textChanged.disconnect(self.change_rect_height)
        self.crop_tools.x_offset_line_edit.textChanged.disconnect(self.change_rect_origin_x)
        self.crop_tools.y_offset_line_edit.textChanged.disconnect(self.change_rect_origin_y)


class RectangleShapeChanger(QObject):
    """Changes the shape of the rectangle"""
    def __init__(self, rectangle: Rectangle):
        super().__init__()
        self.rectangle = rectangle
        self.initial_origin_x_before_pressing = 0
        self.initial_origin_y_before_pressing = 0
        self.initial_width_before_pressing = 0
        self.initial_height_before_pressing = 0

    width_changed_signal = pyqtSignal()
    height_changed_signal = pyqtSignal()
    origin_x_changed_signal = pyqtSignal()
    origin_y_changed_signal = pyqtSignal()

    def change_width(self, width: int):
        """Width changer"""
        self.rectangle.set_width(width)
        self.width_changed_signal.emit()

    def change_height(self, height: int):
        """Height changer"""
        self.rectangle.set_height(height)
        self.height_changed_signal.emit()

    def change_origin_x(self, origin_x: int):
        """Origin x changer"""
        self.rectangle.set_origin_x(origin_x)
        self.origin_x_changed_signal.emit()

    def change_origin_y(self, origin_y: int):
        """Origin y changer"""
        self.rectangle.set_origin_y(origin_y)
        self.origin_y_changed_signal.emit()

    def set_new_shape(self, width: int, height: int, origin_x: int, origin_y: int):
        """New shape setter"""
        self.change_width(width)
        self.change_height(height)
        self.change_origin_x(origin_x)
        self.change_origin_y(origin_y)

    def set_shape_before_pressing(self):
        """Shape setter before the rectangle is pressed"""
        self.initial_origin_x_before_pressing = self.rectangle.origin[0]
        self.initial_origin_y_before_pressing = self.rectangle.origin[1]
        self.initial_width_before_pressing = self.rectangle.size[0]
        self.initial_height_before_pressing = self.rectangle.size[1]

    def reshape_rectangle(self, moved_dist: list):
        """Checks which part of the rectangle is pressed and reshapes the rectangle accordingly"""
        if self.rectangle.hovered_part == RectanglePart.BOTTOM:
            self.change_height(self.initial_height_before_pressing + moved_dist[1])
        elif self.rectangle.hovered_part == RectanglePart.RIGHT:
            self.change_width(self.initial_width_before_pressing + moved_dist[0])
        elif self.rectangle.hovered_part == RectanglePart.LEFT:
            self.change_width(self.initial_width_before_pressing - moved_dist[0])
            self.change_origin_x(self.initial_origin_x_before_pressing + moved_dist[0])
        elif self.rectangle.hovered_part == RectanglePart.TOP:
            self.change_height(self.initial_height_before_pressing - moved_dist[1])
            self.change_origin_y(self.initial_origin_y_before_pressing + moved_dist[1])
        elif self.rectangle.hovered_part == RectanglePart.INSIDE:
            self.change_origin_x(self.initial_origin_x_before_pressing + moved_dist[0])
            self.change_origin_y(self.initial_origin_y_before_pressing + moved_dist[1])
        elif self.rectangle.hovered_part == RectanglePart.TOP_LEFT_CORNER:
            self.change_width(self.initial_width_before_pressing - moved_dist[0])
            self.change_origin_x(self.initial_origin_x_before_pressing + moved_dist[0])
            self.change_height(self.initial_height_before_pressing - moved_dist[1])
            self.change_origin_y(self.initial_origin_y_before_pressing + moved_dist[1])
        elif self.rectangle.hovered_part == RectanglePart.TOP_RIGHT_CORNER:
            self.change_width(self.initial_width_before_pressing + moved_dist[0])
            self.change_height(self.initial_height_before_pressing - moved_dist[1])
            self.change_origin_y(self.initial_origin_y_before_pressing + moved_dist[1])
        elif self.rectangle.hovered_part == RectanglePart.BOTTOM_RIGHT_CORNER:
            self.change_width(self.initial_width_before_pressing + moved_dist[0])
            self.change_height(self.initial_height_before_pressing + moved_dist[1])
        elif self.rectangle.hovered_part == RectanglePart.BOTTOM_LEFT_CORNER:
            self.change_width(self.initial_width_before_pressing - moved_dist[0])
            self.change_origin_x(self.initial_origin_x_before_pressing + moved_dist[0])
            self.change_height(self.initial_height_before_pressing + moved_dist[1])

    def limits_the_size(self):
        """Resizes the rectangle if it gets smaller than its limits"""
        if self.rectangle.size[0] < MIN_WIDTH:
            self.change_width(MIN_WIDTH)
            if self.rectangle.hovered_part == RectanglePart.LEFT or \
                    self.rectangle.hovered_part == RectanglePart.TOP_LEFT_CORNER or \
                    self.rectangle.hovered_part == RectanglePart.BOTTOM_LEFT_CORNER:
                self.change_origin_x(self.initial_origin_x_before_pressing
                                            + self.initial_width_before_pressing
                                            - MIN_WIDTH)
            else:
                self.change_origin_x(self.initial_origin_x_before_pressing)
        if self.rectangle.size[1] < MIN_HEIGHT:
            self.change_height(MIN_HEIGHT)
            if self.rectangle.hovered_part == RectanglePart.TOP or \
                    self.rectangle.hovered_part == RectanglePart.TOP_LEFT_CORNER or \
                    self.rectangle.hovered_part == RectanglePart.TOP_RIGHT_CORNER:
                self.change_origin_y(self.initial_origin_y_before_pressing
                                            + self.initial_height_before_pressing
                                            - MIN_HEIGHT)
            else:
                self.change_origin_y(self.initial_origin_y_before_pressing)

    def out_of_bounds_control(self):
        """Checks if the rectangle gets out of the boundaries and adjusts the shape"""
        if self.rectangle.origin[0] < 0:
            self.rectangle.set_origin_x(0)
            if self.rectangle.hovered_part != RectanglePart.INSIDE:
                self.change_width(self.initial_width_before_pressing
                                  + self.initial_origin_x_before_pressing)
        if self.rectangle.origin[1] < 0:
            self.rectangle.set_origin_y(0)
            if self.rectangle.hovered_part != RectanglePart.INSIDE:
                self.change_height(self.initial_height_before_pressing
                                   + self.initial_origin_y_before_pressing)
        if self.rectangle.origin[0] + self.rectangle.size[0] \
                >= self.rectangle.painter.pixmap.width():
            if self.rectangle.hovered_part != RectanglePart.INSIDE:
                self.change_width(self.rectangle.painter.pixmap.width()
                                  - self.rectangle.origin[0])
            else:
                self.change_origin_x(self.rectangle.painter.pixmap.width()
                                     - self.rectangle.size[0])
        if self.rectangle.origin[1] + self.rectangle.size[1] \
                >= self.rectangle.painter.pixmap.height():
            if self.rectangle.hovered_part != RectanglePart.INSIDE:
                self.change_height(self.rectangle.painter.pixmap.height()
                                   - self.rectangle.origin[1])
            else:
                self.change_origin_y(self.rectangle.painter.pixmap.height()
                                     - self.rectangle.size[1])


class RectanglePart(enum.Enum):
    """Enum that defines the rectangle parts"""
    NONE = 0
    TOP_LEFT_CORNER = 1
    TOP = 2
    TOP_RIGHT_CORNER = 3
    RIGHT = 4
    BOTTOM_RIGHT_CORNER = 5
    BOTTOM = 6
    BOTTOM_LEFT_CORNER = 7
    LEFT = 8
    INSIDE = 9


class RectanglePainter:
    """Manages the rectangle painting"""
    def __init__(self, rect: Rectangle):
        self.rect = rect
        self.pixmap = QPixmap()
        self.pen_dash_line = QPen()
        self.pen_dash_line.setColor(Qt.white)
        self.pen_dash_line.setStyle(Qt.DashLine)
        self.pen_dash_line.setWidth(1)

        self.lines_painter = QPainter()
        self.pen_solid_line = QPen()
        self.pen_solid_line.setColor(Qt.white)
        self.pen_solid_line.setWidth(2)

        self.rect_painter = QPainter()

    def set_pixmap(self, pixmap: QPixmap):
        """Pixmap setter"""
        self.pixmap = pixmap

    def draw_rect(self):
        """Draws the rectangle"""
        self.rect_painter = QPainter(self.pixmap)
        self.rect_painter.setPen(self.pen_solid_line)

        self.rect_painter.drawRect(self.rect.origin[0], self.rect.origin[1],
                                   self.rect.size[0], self.rect.size[1])
        self.rect_painter.end()

    def draw_lines(self):
        """Draws the inner rectangle lines"""
        self.lines_painter = QPainter(self.pixmap)
        self.lines_painter.setPen(self.pen_dash_line)

        self.lines_painter.drawLine(self.rect.origin[0] + self.rect.size[0] / 3,
                                    self.rect.origin[1],
                                    self.rect.origin[0] + self.rect.size[0] / 3,
                                    self.rect.origin[1] + self.rect.size[1])
        self.lines_painter.drawLine(self.rect.origin[0] + self.rect.size[0] * 2 / 3,
                                    self.rect.origin[1],
                                    self.rect.origin[0] + self.rect.size[0] * 2 / 3,
                                    self.rect.origin[1] + self.rect.size[1])
        self.lines_painter.drawLine(self.rect.origin[0],
                                    self.rect.origin[1] + self.rect.size[1] / 3,
                                    self.rect.origin[0] + self.rect.size[0],
                                    self.rect.origin[1] + self.rect.size[1] / 3)
        self.lines_painter.drawLine(self.rect.origin[0],
                                    self.rect.origin[1] + self.rect.size[1] * 2 / 3,
                                    self.rect.origin[0] + self.rect.size[0],
                                    self.rect.origin[1] + self.rect.size[1] * 2 / 3)
        self.lines_painter.end()

    def draw(self):
        """Draws the rectangle and its inner lines"""
        self.draw_rect()
        self.draw_lines()


class SignalReceiver(QObject):
    """Class for managing the received signals"""
    def __init__(self, crop_action_controller: CropActionController, rectangle: Rectangle):
        super().__init__()
        self.rectangle = rectangle
        self.mouse = crop_action_controller.mouse
        self.pixmap = crop_action_controller.model.get_current_pixmap
        self.image_viewer = crop_action_controller.image_viewer
        self.image_view = self.image_viewer.image_view
        self.min_distance_pixels = 10

    @pyqtSlot(QPointF)
    def change_cursor_shape(self, cursor_pos: QPointF):
        """Changes the cursor shape when it hovers on the rectangle"""
        if self.rectangle.origin[0] - self.min_distance_pixels < cursor_pos.x() \
                < self.rectangle.origin[0] + self.min_distance_pixels and \
                self.rectangle.origin[1] - self.min_distance_pixels < cursor_pos.y() \
                < self.rectangle.origin[1] + self.min_distance_pixels:
            self.rectangle.hovered_part = RectanglePart.TOP_LEFT_CORNER
            self.image_view.viewport().setCursor(Qt.SizeFDiagCursor)
        elif self.rectangle.origin[0] - self.min_distance_pixels \
                < cursor_pos.x() - self.rectangle.size[0] \
                < self.rectangle.origin[0] + self.min_distance_pixels and \
                self.rectangle.origin[1] - self.min_distance_pixels < cursor_pos.y() \
                < self.rectangle.origin[1] + self.min_distance_pixels:
            self.rectangle.hovered_part = RectanglePart.TOP_RIGHT_CORNER
            self.image_view.viewport().setCursor(Qt.SizeBDiagCursor)
        elif self.rectangle.origin[0] - self.min_distance_pixels \
                < cursor_pos.x() - self.rectangle.size[0] \
                < self.rectangle.origin[0] + self.min_distance_pixels and \
                self.rectangle.origin[1] - self.min_distance_pixels \
                < cursor_pos.y() - self.rectangle.size[1] \
                < self.rectangle.origin[1] + self.min_distance_pixels:
            self.rectangle.hovered_part = RectanglePart.BOTTOM_RIGHT_CORNER
            self.image_view.viewport().setCursor(Qt.SizeFDiagCursor)
        elif self.rectangle.origin[0] - self.min_distance_pixels < cursor_pos.x() \
                < self.rectangle.origin[0] + self.min_distance_pixels and \
                self.rectangle.origin[1] - self.min_distance_pixels \
                < cursor_pos.y() - self.rectangle.size[1] \
                < self.rectangle.origin[1] + self.min_distance_pixels:
            self.rectangle.hovered_part = RectanglePart.BOTTOM_LEFT_CORNER
            self.image_view.viewport().setCursor(Qt.SizeBDiagCursor)
        elif self.rectangle.origin[1] - self.min_distance_pixels < cursor_pos.y() \
                < self.rectangle.origin[1] + self.min_distance_pixels and \
                self.rectangle.origin[0] < cursor_pos.x() \
                < self.rectangle.origin[0] + self.rectangle.size[0]:
            self.rectangle.hovered_part = RectanglePart.TOP
            self.image_view.viewport().setCursor(Qt.SizeVerCursor)
        elif self.rectangle.origin[1] - self.min_distance_pixels \
                < cursor_pos.y() - self.rectangle.size[1] \
                < self.rectangle.origin[1] + self.min_distance_pixels and \
                self.rectangle.origin[0] < cursor_pos.x() \
                < self.rectangle.origin[0] + self.rectangle.size[0]:
            self.rectangle.hovered_part = RectanglePart.BOTTOM
            self.image_view.viewport().setCursor(Qt.SizeVerCursor)
        elif self.rectangle.origin[0] - self.min_distance_pixels < cursor_pos.x() \
                < self.rectangle.origin[0] + self.min_distance_pixels and \
                self.rectangle.origin[1] < cursor_pos.y() \
                < self.rectangle.origin[1] + self.rectangle.size[1]:
            self.rectangle.hovered_part = RectanglePart.LEFT
            self.image_view.viewport().setCursor(Qt.SizeHorCursor)
        elif self.rectangle.origin[0] - self.min_distance_pixels \
                < cursor_pos.x() - self.rectangle.size[0] \
                < self.rectangle.origin[0] + self.min_distance_pixels and \
                self.rectangle.origin[1] < cursor_pos.y() \
                < self.rectangle.origin[1] + self.rectangle.size[1]:
            self.rectangle.hovered_part = RectanglePart.RIGHT
            self.image_view.viewport().setCursor(Qt.SizeHorCursor)
        elif self.rectangle.origin[0] < cursor_pos.x() \
                < self.rectangle.origin[0] + self.rectangle.size[0] and \
                self.rectangle.origin[1] < cursor_pos.y() \
                < self.rectangle.origin[1] + self.rectangle.size[1]:
            self.rectangle.hovered_part = RectanglePart.INSIDE
            self.image_view.viewport().setCursor(Qt.ClosedHandCursor)
        else:
            self.rectangle.hovered_part = RectanglePart.NONE
            self.image_view.viewport().setCursor(Qt.ArrowCursor)

    @pyqtSlot()
    def mouse_out_of_pixmap(self):
        """Restores the cursor back to the arrow shape when it leaves the pixmap"""
        self.image_view.viewport().setCursor(Qt.ArrowCursor)
        self.mouse.on_pixmap = False

    @pyqtSlot()
    def image_pressed(self):
        """Receives a signal when the image is pressed"""
        if self.rectangle.hovered_part != RectanglePart.NONE:
            self.rectangle.shape_changer.set_shape_before_pressing()

    @pyqtSlot(list)
    def change_rect(self, moved_dist: list):
        """Receives a signal when the rectangle changes its shape"""
        self.rectangle.shape_changer.reshape_rectangle(moved_dist)
        self.rectangle.shape_changer.limits_the_size()
        self.rectangle.shape_changer.out_of_bounds_control()
        self.rectangle.display_rect()

    @pyqtSlot()
    def mouse_entered_the_pixmap(self):
        """Slot that receives a signal when the mouse is on the pixmap"""
        self.mouse.on_pixmap = True


class CropMouseListener(MouseListener):
    """Class for managing mouse events"""
    def __init__(self, rectangle: Rectangle):
        super().__init__()
        self.rectangle = rectangle

    pressed_moving_signal = pyqtSignal(list)

    def on_move(self, pos_x, pos_y):
        """On move event listener"""
        if self.on_pixmap and self.pressed and self.rectangle.hovered_part != RectanglePart.NONE:
            moved_x = pos_x - self.initial_pos[0]
            moved_y = pos_y - self.initial_pos[1]
            if moved_x != self.moved_dist[0] or moved_y != self.moved_dist[1]:
                self.moved_dist[1] = moved_y
                self.moved_dist[0] = moved_x
                self.pressed_moving_signal.emit(self.moved_dist)

    def on_click(self, pos_x, pos_y, _, pressed):
        """On click event listener"""
        if pressed:
            self.initial_pos = [pos_x, pos_y]
        self.pressed = pressed
