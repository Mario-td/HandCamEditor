"""Draw model file"""
import dataclasses
from typing import Optional

import cv2
import numpy as np
from PyQt5.QtCore import QPointF
from PyQt5.QtGui import QColor, QPixmap

from ..image_filter import ImageFilterContainer
from ..shape_painter import ShapePainterContainer, RhombusPainter, \
    CirclePainter, SquarePainter, SprayEffect
from ..utils import image_to_pixmap

from .editing_tool import EditingToolModel


class DrawActionModel(EditingToolModel):
    """Controller of the drawing action"""

    def __init__(self, img_editor: 'ImageEditor'):
        super().__init__(img_editor)
        self.image_painter = ImagePainter(self.image_editor.tmp_img,
                                          self.image_editor.tmp_img,
                                          self.image_editor.tmp_img)
        self.brush_size = 30
        self.filter_container = None

    def create_new_image_painter(self):
        """Creates an image painter and updates the temporary image"""
        self.image_editor.create_temp_image()
        self.image_painter.__init__(self.image_editor.tmp_img.copy(),
                                    np.zeros(self.image_editor.tmp_img.shape, dtype=np.uint8),
                                    self.image_editor.get_current_image())
        self.image_editor.tmp_img = self.image_painter.images_container.img

    def update_image_painter_using_filter(self, filter_name: str):
        """Creates an image painter which uses a filter to paint"""
        self.image_editor.tmp_img = self.image_painter.images_container.img
        painter_shape: str = self.image_painter.shape_container.get_shape_name()
        self.image_painter.__init__(self.image_editor.tmp_img.copy(),
                                    self.filter_container.get_filtered_image(filter_name),
                                    self.image_editor.get_current_image())
        self.image_painter.shape_container.set_shape(painter_shape)

    def update_image_painter_using_color(self, color: QColor):
        """Creates an image painter which uses a specific colour"""
        self.image_editor.tmp_img = self.image_painter.images_container.img
        color_image = np.zeros(self.image_editor.tmp_img.shape, dtype=np.uint8)
        color_image[:, :] = (color.getRgb()[2], color.getRgb()[1], color.getRgb()[0])
        painter_shape: str = self.image_painter.shape_container.get_shape_name()
        self.image_painter.__init__(self.image_editor.tmp_img.copy(),
                                    color_image,
                                    self.image_editor.get_current_image())

        self.image_painter.shape_container.set_shape(painter_shape)

    def change_painter_shape(self, shape_name):
        """Changes the image painter shape"""
        self.image_painter.shape_container.set_shape(shape_name)

    def set_filters(self, filter_container: ImageFilterContainer):
        """Image container setter"""
        self.filter_container = filter_container

    def change_brush_size(self, size: int):
        """Changes the size of the painter brush"""
        self.brush_size = size
        self.image_painter.change_brush_size(size)

    def set_brush_size_from_model(self):
        """Sets the shape that is displayed in the spin"""
        self.image_painter.shape_container.set_size(self.brush_size)


@dataclasses.dataclass
class PainterImagesContainer:
    """Class that contains the images that are used in the image painter"""
    img: np.ndarray
    first_img_history: np.ndarray
    edited_image: np.ndarray
    original_image: Optional[np.ndarray] = None

    def __post_init__(self):
        self.original_image = self.img.copy()

    def reset_original_image(self):
        """Substitutes the current image by the original one, without edition"""
        self.img = self.original_image.copy()


class ImagePainter:
    """Handles the actions for editing the image."""

    def __init__(self, img, edited_image, first_img_history):
        self.images_container = PainterImagesContainer(img=img,
                                                       edited_image=edited_image,
                                                       first_img_history=first_img_history)

        self.edited_image_mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
        self.erase_image_mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)
        self.cursor_mask = np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

        self.erase: bool = False

        self.shape_container = ShapePainterContainer()
        self.shape_container.append_painter('Rhombus', RhombusPainter(30))
        self.shape_container.append_painter('Spray', SprayEffect(30))
        self.shape_container.append_painter('Circle', CirclePainter(30))
        self.shape_container.append_painter('Square', SquarePainter(30))
        self.shape_container.set_shape('Spray')

    def edit_image(self, cursor_pos: QPointF, paint: bool):
        """Applies the filter in the area if the action is clicking or it draws the cursor
        if the action is hovering"""

        if paint:
            mask = self.edited_image_mask
        else:
            mask = self.cursor_mask

        self.shape_container.draw_shape(mask, (int(cursor_pos.x()), int(cursor_pos.y())),
                                        (255, 0, 0))

        cv2.copyTo(self.images_container.edited_image, mask, self.images_container.img)
        if self.erase:
            cv2.copyTo(self.images_container.first_img_history, mask, self.images_container.img)

    def get_edited_img_pixmap(self) -> QPixmap:
        """Edited pixmap getter"""
        return image_to_pixmap(self.images_container.img)

    def remove_cursor(self):
        """Removes the cursor from the image"""
        self.images_container.reset_original_image()
        self.cursor_mask = np.zeros((self.images_container.img.shape[0],
                                     self.images_container.img.shape[1]),
                                    dtype=np.uint8)
        if self.erase:
            cv2.copyTo(self.images_container.first_img_history,
                       self.edited_image_mask,
                       self.images_container.img)
            return
        cv2.copyTo(self.images_container.edited_image,
                   self.edited_image_mask,
                   self.images_container.img)

    def activate_eraser(self):
        """Activates the eraser to remove what it was painted"""
        shape_name = self.shape_container.shape_name
        size = self.shape_container.get_size()
        self.__init__(self.images_container.img,
                      self.images_container.edited_image,
                      self.images_container.first_img_history)
        self.shape_container.set_shape(shape_name)
        self.shape_container.set_size(size)
        self.erase = True

    def change_brush_size(self, size: int):
        """Changes the size of the brush"""
        self.shape_container.set_size(size)
