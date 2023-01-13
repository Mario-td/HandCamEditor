"""Image filters"""
from abc import ABC, abstractmethod
import cv2
import numpy as np

from .utils import image_to_pixmap


class ImageFilter(ABC):
    """Abstract class of the filters"""
    def __init__(self, filter_name):
        self.filter_name = filter_name

    def get_filter_name(self) -> str:
        """Filter name getter"""
        return self.filter_name

    @abstractmethod
    def apply_filter(self, image: np.ndarray) -> np.ndarray:
        """Applies the filter on a given image"""


class ImageFilterContainer:
    """Filtered image container"""
    def __init__(self):
        self.filter_functions = {}
        self.filtered_images = {}
        self.pixmap_filtered_images = {}

    def __len__(self):
        return len(self.filter_functions)

    def append(self, image_filter: ImageFilter):
        """Appends a filter to the container"""
        self.filter_functions[image_filter.get_filter_name()] = image_filter.apply_filter

    def apply_filters(self, image: np.ndarray):
        """Applies all the filters on a given image"""
        for name, function in self.filter_functions.items():
            self.filtered_images[name] = function(image)

    def get_filtered_image(self, filter_name: str) -> np.ndarray:
        """Filtered image getter"""
        try:
            return self.filtered_images[filter_name]
        except KeyError as err:
            print(f'There is no filter with name {err}')
            return np.zeros((1, 1, 3), np.uint8)

    def get_filtered_images_pixmap(self) -> dict:
        """Filtered pixmap getter"""
        for filter_name, filtered_image in self.filtered_images.items():
            self.pixmap_filtered_images[filter_name] = image_to_pixmap(filtered_image)
        return self.pixmap_filtered_images


class ColormapFilter(ImageFilter):
    """Colormap filter"""
    def __init__(self, filter_name, colormap):
        super().__init__(filter_name)
        self.colormap = colormap

    def apply_filter(self, image: np.ndarray) -> np.ndarray:
        """Returns an image after applying a colormap"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.applyColorMap(gray, self.colormap)


class SketchFilter(ImageFilter):
    """Sketch Filter"""
    def __init__(self):
        super().__init__('SKETCH')

    def apply_filter(self, image: np.ndarray) -> np.ndarray:
        """Returns the sketch effect of images."""
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])
        sharpen_img = cv2.filter2D(image, -1, kernel)
        gray = cv2.cvtColor(sharpen_img, cv2.COLOR_BGR2GRAY)

        inverse_img = 255 - gray
        blurred_img = cv2.GaussianBlur(inverse_img, (11, 11), 0)

        return cv2.cvtColor(cv2.divide(gray, 255 - blurred_img, scale=256), cv2.COLOR_GRAY2RGB)


class CartoonFilter(ImageFilter):
    """Cartoon Filter"""
    def __init__(self):
        super().__init__('CARTOON')
        self.sketch_filter = SketchFilter()

    def apply_filter(self, image: np.ndarray) -> np.ndarray:
        """Returns a cartoon effect in images."""
        image_copy = image.copy()
        edges = self.sketch_filter.apply_filter(image_copy)

        small_image = cv2.pyrDown(image_copy)
        rep = 11
        for _ in range(rep):
            tmp = cv2.bilateralFilter(small_image, d=9, sigmaColor=9, sigmaSpace=7)
            small_image = cv2.bilateralFilter(tmp, d=9, sigmaColor=9, sigmaSpace=7)

        height, width, _ = edges.shape
        image_copy = cv2.pyrUp(small_image, dstsize=(width, height))

        return cv2.bitwise_and(image_copy, edges)


class GrayScaleFilter(ImageFilter):
    """Gray Scale Filter"""
    def __init__(self):
        super().__init__('GRAY')

    def apply_filter(self, image: np.ndarray) -> np.ndarray:
        """Returns the sketch effect of images."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
