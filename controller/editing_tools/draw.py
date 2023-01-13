"""Crop controller file"""
from PyQt5.QtCore import QPointF, Qt, pyqtSignal, QObject
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMessageBox, QColorDialog

from controller.editing_tools import EditingTool
from controller.editing_tools.editing_tool import ButtonContainerController
from controller.image_viewer import ImageViewerController
from controller.mouse_listener import MouseListener
from model.editing_tools import DrawActionModel, FilterActionModel
from model.shape_painter import MINIMUM_BRUSH_SIZE, MAXIMUM_BRUSH_SIZE
from view.accept_cancel import AcceptCancelContainer
from view.editing_tools.draw import DrawAction, EffectAction


class DrawActionController(EditingTool):
    """Controller of the drawing action"""
    def __init__(self, view, model, draw_action: DrawAction):
        super().__init__(view, model, draw_action)
        self.draw_model: DrawActionModel = model.actions['Draw']

        self.image_viewer = view.image_viewer

        self.mouse_listener = DrawMouseListener()

        self.signal_receiver = SignalReceiver(self, self.mouse_listener)

        self.draw_tools_controller = DrawToolsController(view, model, draw_action)

        self.connect_signals()

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view,  'Information', 'Nothing to draw')
            return
        self.draw_model.create_new_image_painter()
        self.action.display_items()
        self.connect_signals_between_elements(True)
        self.draw_model.image_painter.drawn_image = False
        self.accept_action.setDisabled(True)
        self.draw_tools_controller.\
            brush_shape_controller.configure_spinbox(self.draw_model.brush_size)
        self.draw_model.set_brush_size_from_model()

    def connect_signals_between_elements(self, activate: bool):
        """"Method for connecting signals between components"""
        if activate:
            self.image_viewer.signal_sender. \
                enter_image_signal.connect(self.signal_receiver.mouse_entered_the_pixmap)
            self.image_viewer.signal_sender. \
                image_coordinate_signal.connect(self.signal_receiver.cursor_on_pixmap)
            self.image_viewer.signal_sender. \
                leave_image_signal.connect(self.signal_receiver.mouse_out_of_pixmap)
            self.image_viewer.signal_sender. \
                mouse_pressed_image_signal_coordinate.connect(self.signal_receiver.image_pressed)
            self.image_viewer.signal_sender. \
                mouse_pressed_image_signal_coordinate.connect(self.enable_accept_button)
            self.mouse_listener.construct_listener()
            self.mouse_listener.press_image_signal.connect(self.signal_receiver.paint_on_image)
        else:
            self.image_viewer.signal_sender. \
                enter_image_signal.disconnect(self.signal_receiver.mouse_entered_the_pixmap)
            self.image_viewer.signal_sender.image_coordinate_signal. \
                disconnect(self.signal_receiver.cursor_on_pixmap)
            self.image_viewer.signal_sender. \
                leave_image_signal.disconnect(self.signal_receiver.mouse_out_of_pixmap)
            self.image_viewer.signal_sender. \
                mouse_pressed_image_signal_coordinate.disconnect(self.enable_accept_button)
            self.image_viewer.signal_sender.mouse_pressed_image_signal_coordinate. \
                disconnect(self.signal_receiver.image_pressed)
            self.mouse_listener.destroy_listener()
            self.mouse_listener.press_image_signal.disconnect(self.signal_receiver.paint_on_image)

    def accept_edited_image(self):
        """Updates the temporary image and updates the element that displays it"""
        self.model.tmp_img = self.draw_model.image_painter.images_container.img
        self.accept_cancel_controller.accept_and_update_image()

    def connect_signals(self):
        """Method for connecting signals"""
        self.cancel_action.triggered.connect(self.connect_signals_between_elements, False)
        self.accept_action.triggered.connect(self.connect_signals_between_elements, False)
        self.accept_action.triggered.connect(lambda: self.accept_edited_image())
        self.accept_action.triggered. \
            disconnect(self.accept_cancel_controller.accept_and_update_image)

    def enable_accept_button(self):
        """Enables the accept button after painting something on the image"""
        self.draw_model.image_painter.drawn_image = True
        self.accept_action.setEnabled(True)


class DrawMouseListener(MouseListener):
    """Listens to the mouse events to update the image"""

    press_image_signal = pyqtSignal(QPointF, bool)

    def on_move(self, pos_x, pos_y):
        if self.pressed and self.on_pixmap:
            moved_x = pos_x - self.initial_pos[0]
            moved_y = pos_y - self.initial_pos[1]
            self.press_image_signal.emit(QPointF(moved_x + self.initial_pressed_coordinate.x(),
                                                 moved_y + self.initial_pressed_coordinate.y()),
                                         False)

    def on_click(self, pos_x, pos_y, _, pressed):
        if pressed:
            self.initial_pos = [pos_x, pos_y]
        self.pressed = pressed

    def set_initial_pressed_coordinate(self, cursor_pos: QPointF):
        """Sets the initial coordinate where the mouse clicked"""
        self.initial_pressed_coordinate = cursor_pos


class SignalReceiver:
    """Class for managing the received signals"""
    def __init__(self, draw_action_controller: DrawActionController,
                 mouse_listener: DrawMouseListener):
        self.image_viewer_controller = \
            ImageViewerController(draw_action_controller.view, draw_action_controller.model)
        self.image_viewer = draw_action_controller.image_viewer
        self.mouse_listener = mouse_listener
        self.draw_model: DrawActionModel = self.image_viewer_controller.model.actions['Draw']

    def cursor_on_pixmap(self, cursor_pos: QPointF):
        """Changes the cursor shape when it hovers on the pixmap and draws the cursor"""
        self.mouse_listener.on_pixmap = True
        self.paint_on_image(cursor_pos=cursor_pos, hover=True)
        self.draw_model.image_painter.remove_cursor()

    def image_pressed(self, cursor_pos: QPointF):
        """Receives a signal when the image is pressed and paints on the picture"""
        self.mouse_listener.pressed = True
        self.paint_on_image(cursor_pos=cursor_pos, hover=False)
        self.mouse_listener.set_initial_pressed_coordinate(cursor_pos)

    def paint_on_image(self, cursor_pos: QPointF, hover: bool):
        """Updates the image and displays it"""
        self.draw_model.image_painter.edit_image(cursor_pos, paint=not hover)
        self.image_viewer_controller.\
            display_image(self.draw_model.image_painter.get_edited_img_pixmap)

    def mouse_entered_the_pixmap(self):
        """Slot that receives a signal when the mouse is on the pixmap
        and changes its shape"""
        self.image_viewer.image_view.viewport().setCursor(Qt.BlankCursor)

    def mouse_out_of_pixmap(self):
        """Restores the cursor back to the arrow shape when it leaves the pixmap"""
        self.mouse_listener.on_pixmap = False
        self.image_viewer.image_view.viewport().setCursor(Qt.ArrowCursor)
        self.image_viewer_controller.\
            display_image(self.draw_model.image_painter.get_edited_img_pixmap)


class BrushShapeController:
    """Controller of the brush shape actions"""
    def __init__(self, view, model, draw_action: DrawAction):
        self.draw_action = draw_action
        self.brush_shape_container = draw_action.draw_tools.brush_shape_container
        self.view = view
        self.model = model
        self.draw_model: DrawActionModel = self.model.actions['Draw']

        self.connect_action_signals_to_slots()

    def connect_action_signals_to_slots(self):
        """Connects the brush shapes with the slots"""
        change_painter_shape_func = self.draw_model.change_painter_shape

        def connect_each_brush_action(action):
            action.triggered.connect(lambda: change_painter_shape_func(action.text()))

        [connect_each_brush_action(action) for action in self.brush_shape_container]

    def connect_spinbox_signal(self):
        """Connects the spinbox signal, so the brush can change with it"""
        try:
            self.draw_action.draw_tools.size_spinbox.valueChanged.disconnect(self.change_brush_size)
        except TypeError:
            self.draw_action.draw_tools.size_spinbox.valueChanged.connect(self.change_brush_size)

    def change_brush_size(self):
        """Sets the brush size that is displayed in the spinbox"""
        self.draw_model.change_brush_size(self.draw_action.draw_tools.size_spinbox.value())

    def configure_spinbox(self, value: int):
        """Configures the spinbox"""
        self.draw_action.draw_tools.size_spinbox.setMinimum(MINIMUM_BRUSH_SIZE)
        self.draw_action.draw_tools.size_spinbox.setMaximum(MAXIMUM_BRUSH_SIZE)
        self.connect_spinbox_signal()
        self.draw_action.draw_tools.size_spinbox.setValue(value)


class EffectActionController:
    """Controller of the effect action"""
    def __init__(self, view, model, draw_action: DrawAction):
        self.draw_action = draw_action
        self.effect_action = draw_action.draw_tools.effect
        self.view = view
        self.model = model
        self.draw_model: DrawActionModel = self.model.actions['Draw']

        self.cancel_effect_controller = \
            CancelControllerDraw(model,
                                 self.draw_action, draw_action.draw_tools.effect.cancel_effect)
        self.filter_button_container_controller = \
            FilterButtonContainerControllerEffect(self.view, self.model,
                                                  self.effect_action, self.cancel_effect_controller)

    def display_filter_buttons(self):
        """Displays the filter buttons"""
        self.draw_model.filter_container.\
            apply_filters(self.draw_model.image_painter.images_container.img)
        self.effect_action.display_filter_buttons(
            self.draw_model.filter_container.get_filtered_images_pixmap())


class CancelControllerDraw(QObject):
    """Controller of the cancel action"""
    def __init__(self, model, draw_action: DrawAction, cancel_action: AcceptCancelContainer):
        super().__init__()
        self.draw_model: DrawActionModel = model.actions['Draw']
        self.draw_action = draw_action
        self.cancel_action_view = cancel_action
        self.accept_action = self.cancel_action_view.get_accept_action()
        self.accept_action.setVisible(False)
        self.cancel_action = self.cancel_action_view.get_cancel_action()

        self.connect_action_signals()

    pressed_cancel_signal = pyqtSignal(int)

    def connect_action_signals(self):
        """Connects actions to slots"""
        self.cancel_action.triggered.connect(self.trigger_draw_action)

    def trigger_draw_action(self):
        """Triggers the draw action"""
        self.draw_action.toolbar.clear()
        self.draw_action.add_widgets_and_actions_to_toolbar()
        if self.draw_model.image_painter.drawn_image:
            self.draw_action.accept_and_cancel.accept_action.setDisabled(False)
        self.pressed_cancel_signal.emit(self.draw_model.brush_size)


class FilterButtonContainerControllerEffect(ButtonContainerController):
    """Controller of the filter buttons container"""
    def __init__(self, view, model,
                 effect_action: EffectAction, cancel_controller: CancelControllerDraw):
        self.draw_model: DrawActionModel = model.actions['Draw']
        self.filter_model: FilterActionModel = model.actions['Filter']
        super().__init__(view, model, effect_action)
        self.cancel_action = cancel_controller.cancel_action

    def connect_button_signals_to_slots(self):
        """Connects a button to a specific filter"""
        brush_effect = self.draw_model.update_image_painter_using_filter
        trigger_cancel_action = self.trigger_cancel_action

        def connect(button):
            button.clicked.connect(lambda: brush_effect(button.toolTip()))
            button.clicked.connect(lambda: trigger_cancel_action())

        [connect(button) for button in self.button_container.buttons]

    def initialize_filter_buttons(self):
        """Initial setup of the components"""
        self.button_container.populate_buttons(
            len(self.filter_model.filter_container))

    def trigger_cancel_action(self):
        """Triggers the cancel action"""
        self.cancel_action.trigger()


class EraseActionController:
    """Controller of the eraser action"""
    def __init__(self, view, model, draw_action: DrawAction):
        self.draw_action = draw_action
        self.erase_action = draw_action.draw_tools.erase
        self.view = view
        self.model = model
        self.draw_model: DrawActionModel = self.model.actions['Draw']

        self.connect_action_signals_to_slots()

    def connect_action_signals_to_slots(self):
        """Connects actions to slots"""
        self.erase_action.triggered.connect(self.draw_model.image_painter.activate_eraser)


class DrawToolsController:
    """Controller of the draw tools"""
    def __init__(self, view, model, draw_action: DrawAction):
        self.draw_action = draw_action
        self.effect_action_controller = EffectActionController(view, model, self.draw_action)
        self.brush_shape_controller = BrushShapeController(view, model, self.draw_action)
        self.erase_controller = EraseActionController(view, model, self.draw_action)

        self.draw_model: DrawActionModel = model.actions['Draw']

        self.color = QColor(255, 255, 255, 255)

        self.color_picker = QColorDialog(self.color)

        self.connect_signals()

    def connect_signals(self):
        """Connects actions to slots"""
        self.draw_action.draw_tools.color.triggered.connect(self.on_click_color)
        self.draw_action.draw_tools.effect.triggered.connect(self.on_click_effect)
        self.effect_action_controller.cancel_effect_controller.\
            pressed_cancel_signal.connect(self.brush_shape_controller.configure_spinbox)

    def on_click_color(self):
        """Method triggered when the color action is pressed"""
        self.open_color_dialog()
        self.draw_model.set_brush_size_from_model()

    def on_click_effect(self):
        """Method triggered when the effect action is pressed"""
        self.effect_action_controller.display_filter_buttons()

    def open_color_dialog(self):
        """Opens the color dialog"""
        color = self.color_picker.getColor(self.color)
        if color.isValid():
            self.draw_model.update_image_painter_using_color(color)
            self.color = color
