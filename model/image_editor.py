"""Image editor logic"""
from PyQt5.QtGui import QPixmap
import numpy as np
import cv2

from .editing_tools import CropActionModel, ResizeActionModel, \
    RotationActionModel, FilterActionModel, DrawActionModel, \
    AdjustActionModel, StyleTransferActionModel, DeepDreamActionModel
from .utils import image_to_pixmap

from .image_filter import ImageFilterContainer, SketchFilter, \
    CartoonFilter, GrayScaleFilter, ColormapFilter


class ImageEditor:
    """Handles the actions for editing the image."""
    def __init__(self):
        self.history_img = []
        self.idx_current_img = 0

        self.tmp_img = np.zeros((1, 1, 3), np.uint8)

        filter_container = ImageFilterContainer()
        filter_container.append(SketchFilter())
        filter_container.append(CartoonFilter())
        filter_container.append(GrayScaleFilter())
        filter_container.append(ColormapFilter('SPRING', cv2.COLORMAP_SPRING))
        filter_container.append(ColormapFilter('HOT', cv2.COLORMAP_HOT))
        filter_container.append(ColormapFilter('HSV', cv2.COLORMAP_HSV))
        filter_container.append(ColormapFilter('JET', cv2.COLORMAP_JET))
        filter_container.append(ColormapFilter('PINK', cv2.COLORMAP_PINK))
        filter_container.append(ColormapFilter('COOL', cv2.COLORMAP_COOL))
        filter_container.append(ColormapFilter('SUMMER', cv2.COLORMAP_SUMMER))
        filter_container.append(ColormapFilter('WINTER', cv2.COLORMAP_WINTER))
        filter_container.append(ColormapFilter('OCEAN', cv2.COLORMAP_OCEAN))
        filter_container.append(ColormapFilter('RAINBOW', cv2.COLORMAP_RAINBOW))

        self.actions = {'Crop': CropActionModel(self),
                        'Resize': ResizeActionModel(self),
                        'Rotation': RotationActionModel(self),
                        'Filter': FilterActionModel(self),
                        'Draw': DrawActionModel(self),
                        'Adjust': AdjustActionModel(self),
                        'Style Transfer': StyleTransferActionModel(self),
                        'Deep Dream': DeepDreamActionModel(self)}

        self.actions['Draw'].set_filters(filter_container)
        self.actions['Filter'].set_filters(filter_container)

    def __bool__(self):
        return bool(self.history_img)

    def load_image(self, file_path: str):
        """Loads a new image"""
        self.idx_current_img = 0
        self.history_img.clear()
        self.history_img.append(cv2.imread(file_path))

    def save_image_as(self, file_path: str):
        """Saves the image"""
        cv2.imwrite(file_path, self.get_current_image())

    def insert_new_image(self):
        """Inserts a new image in the history"""
        if self.idx_current_img == len(self.history_img) - 1:
            self.history_img.append(self.tmp_img)
            self.idx_current_img += 1
            return
        self.idx_current_img += 1
        self.history_img[self.idx_current_img] = self.tmp_img
        del self.history_img[self.idx_current_img+1:]

    def undo_image(self):
        """Undoes the image from the history"""
        if self.idx_current_img > 0:
            self.idx_current_img -= 1

    def redo_image(self):
        """Redoes the image from the history"""
        if self.idx_current_img < len(self.history_img) - 1:
            self.idx_current_img += 1

    def create_temp_image(self):
        """Creates a temporary image"""
        self.tmp_img = self.get_current_image()

    def set_temp_image(self, image: np.ndarray):
        """Temporary setter"""
        self.tmp_img = image

    def get_current_image_size(self) -> (int, int):
        """Current image size getter, height and width"""
        current_image = self.get_current_image()
        return current_image.shape[:2]

    def get_temp_pixmap(self) -> QPixmap:
        """Temporary pixmap getter"""
        return image_to_pixmap(self.tmp_img)

    def get_current_image(self) -> np.ndarray:
        """Current image getter"""
        return self.history_img[self.idx_current_img]

    def set_current_image(self, image: np.ndarray) -> None:
        """Current image setter"""
        self.history_img[self.idx_current_img] = image

    def get_current_pixmap(self) -> QPixmap:
        """Current pixmap getter"""
        return image_to_pixmap(self.get_current_image())
