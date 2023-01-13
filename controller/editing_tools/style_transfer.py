"""Style transfer action controller module"""
from threading import Thread

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QPushButton, QApplication
from PyQt5.QtCore import Qt

from controller.editing_tools import EditingTool
from controller.editing_tools.editing_tool import ButtonContainerController
from controller.image_viewer import ImageViewerController
from model.editing_tools import StyleTransferActionModel
from view.editing_tools.style_transfer import StyleTransferAction


class StyleTransferActionController(EditingTool):
    """Controller of the style controller action"""
    def __init__(self, view, model, style_transfer_action: StyleTransferAction):
        super().__init__(view, model, style_transfer_action)
        self.view = view
        self.model = model
        self.style_transfer_model: StyleTransferActionModel = model.actions['Style Transfer']
        self.style_transfer_tools_controller = StyleTransferToolsController(view,
                                                                            model,
                                                                            style_transfer_action)

    def show_tools(self):
        if not self.model:
            QMessageBox(self.view).information(self.view, 'Information',
                                               'Nothing to transfer style')
            return
        self.model.create_temp_image()
        self.style_transfer_tools_controller.initialize_components()
        self.action.display_items()


class StyleTransferToolsController:
    """Controller of the transfer style tools"""
    def __init__(self, view, model, action: StyleTransferAction):
        self.view = view
        self.model = model
        self.style_transfer_model: StyleTransferActionModel = model.actions['Style Transfer']
        self.style_action = action
        self.button_container_view = self.style_action.style_transfer_tools.button_container
        self.button_container_controller = StyleTransferButtonContainerController(view,
                                                                                  model,
                                                                                  action)
        self.add_styled_image_button = self.style_action.\
            style_transfer_tools.add_styled_image_button

    def initialize_components(self):
        """Initializes the buttons"""
        self.button_container_controller.update_button_images()
        self.connect_button_signals_to_slots()

    def add_image(self):
        """Opens a new image"""
        dialog = QFileDialog()
        dialog.setWindowTitle('Add Style Image')
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter('Images (*.png *.bmp *.jpg)')
        if dialog.exec():
            file_path = dialog.selectedFiles()
            self.style_transfer_model.add_styled_image_directory((file_path[0]))
            image_name = self.style_transfer_model.path_leaf(file_path[0])
            self.button_container_view.\
                add_button(image_name,
                           self.style_transfer_model.get_filter_image_pixmap(image_name))
            self.button_container_controller.connect(self.button_container_view.buttons[-1])

    def connect_button_signals_to_slots(self):
        """Method for connecting al the buttons"""
        self.button_container_controller.connect_button_signals_to_slots()
        try:
            self.add_styled_image_button.triggered.disconnect(self.add_image)
            self.add_styled_image_button.triggered.connect(self.add_image)
        except TypeError:
            self.add_styled_image_button.triggered.connect(self.add_image)


class StyleTransferButtonContainerController(ButtonContainerController):
    """Contains the button filters controller"""

    def __init__(self, view, model, action: StyleTransferAction):
        self.style_transfer_model: StyleTransferActionModel = model.actions['Style Transfer']
        self.style_transfer_view = action
        self.connected_signals = False
        super().__init__(view, model, action.style_transfer_tools)
        self.image_viewer_controller = ImageViewerController(view, model)
        self.styled_image_thread = Thread(target=self.style_transfer_model.
                                          apply_style_transfer,
                                          args=('',))

    def display_styled_image(self, style_name: str):
        """Method that initializes the thread for transferring the style"""
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.view.tool_bar.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.styled_image_thread = Thread(target=self.style_transfer_model.
                                          apply_style_transfer,
                                          args=(style_name,
                                                self.model.get_current_image(),))
        self.styled_image_thread.start()

    def styled_image_slot(self):
        """Method to update the displayed image and join the thread"""
        self.image_viewer_controller.display_image()
        self.styled_image_thread.join()
        QApplication.restoreOverrideCursor()
        self.view.tool_bar.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.style_transfer_view.accept_and_cancel.accept_action.setEnabled(True)

    def connect(self, button: QPushButton):
        """Connects every action for applying the style transfer"""
        button.clicked.connect(lambda: self.display_styled_image(button.toolTip()))

    def connect_button_signals_to_slots(self):
        """Method for connecting all the button signals"""
        connect = self.connect
        styled_image_slot = self.styled_image_slot
        if not self.connected_signals:
            [connect(button) for button in self.button_container.buttons]
            self.style_transfer_model.\
                signal_sender.style_transfer_finished.connect(styled_image_slot)
            self.connected_signals = True

    def update_button_images(self):
        """Method for updating the button images"""
        self.button_container.\
            update_button_image(self.style_transfer_model.get_all_filtered_images_pixmap())

    def initialize_filter_buttons(self):
        """Method for initializing the button images"""
        self.button_container.populate_buttons(
            len(self.style_transfer_model.styled_images_directories))
