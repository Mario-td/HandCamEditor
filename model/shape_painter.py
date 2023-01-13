"""Shape painter model file"""
import dataclasses
from abc import ABC, abstractmethod
from typing import Optional

import numpy as np
import cv2
from mypy_extensions import TypedDict

MINIMUM_BRUSH_SIZE = 10
MAXIMUM_BRUSH_SIZE = 100


class ShapePainter(ABC):
    """Shape painter abstract class"""
    def __init__(self, size: int):
        self.size: int = size

    def set_size(self, size: int):
        """Size setter"""
        self.size = size

    def get_size(self) -> int:
        """Size getter"""
        return self.size

    @abstractmethod
    def draw_on_image(self, img: np.ndarray, center_position: tuple, color: tuple):
        """Draws the shape on the image"""


class RhombusPainter(ShapePainter):
    """Rhombus shape"""
    def __init__(self, size: int):
        super().__init__(size * 2)

    def set_size(self, size: int):
        self.size = size * 2

    def get_size(self) -> int:
        return int(self.size / 2)

    def draw_on_image(self, img: np.ndarray, center_position: tuple, color: tuple):
        pts = np.array([[center_position[0] - int(self.size / 2), center_position[1]],
                        [center_position[0], center_position[1] - int(self.size / 2)],
                        [center_position[0] + int(self.size / 2), center_position[1]],
                        [center_position[0], center_position[1] + int(self.size / 2)]],
                       np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(img, [pts], color)


class SprayEffect(ShapePainter):
    """Spray effect shape"""
    def __init__(self, radius: int):
        super().__init__(radius)
        self.points_number = int(np.pi * (self.size ^ 2) * 0.75)

    def set_size(self, size: int):
        self.size = size
        self.points_number = int(np.pi * (self.size ^ 2) * 0.75)

    def draw_on_image(self, img: np.ndarray, center_position: tuple, color: tuple):
        minimum_radius_offset = int(self.size * 0.15)
        for _ in range(self.points_number):
            random_radius = np.random.randint(minimum_radius_offset, self.size + 1)
            random_degree = np.random.randint(360)

            x_coordinate = int(random_radius * np.cos(np.radians(random_degree)))
            y_coordinate = int(random_radius * np.sin(np.radians(random_degree)))

            cv2.circle(img, (center_position[0] + x_coordinate, center_position[1] + y_coordinate),
                       0, color, cv2.FILLED)


class CirclePainter(ShapePainter):
    """Circle shape"""
    def draw_on_image(self, img: np.ndarray, center_position: tuple, color: tuple):
        cv2.circle(img, (center_position[0], center_position[1]),
                   self.size, color, cv2.FILLED)


class SquarePainter(ShapePainter):
    """Square shape"""
    def __init__(self, size: int):
        super().__init__(size * 2)

    def set_size(self, size: int):
        self.size = size * 2

    def get_size(self) -> int:
        return int(self.size / 2)

    def draw_on_image(self, img: np.ndarray, center_position: tuple, color: tuple):
        cv2.rectangle(img, (center_position[0] - int(self.size / 2),
                            center_position[1] - int(self.size / 2)),
                      (center_position[0] + int(self.size / 2),
                       center_position[1] + int(self.size / 2)), (255, 0, 0), -1)


class ShapePainterDict(TypedDict):
    """Shape painter dictionary"""
    name: str
    shape_painter: ShapePainter


@dataclasses.dataclass
class ShapePainterContainer:
    """Strategy container of shape painters"""

    shape_painter_dict = ShapePainterDict()
    current_shape_painter: Optional[ShapePainter] = None
    shape_name: str = ""

    def append_painter(self, shape_name: str, shape_painter: ShapePainter):
        """Appends a new shape painter"""
        self.shape_painter_dict[shape_name] = shape_painter

    def set_shape(self, shape_name):
        """Sets the shape painter"""
        self.shape_name = shape_name
        self.current_shape_painter = self.shape_painter_dict[self.shape_name]

    def get_shape_name(self) -> str:
        """Sets the shape painter"""
        return self.shape_name

    def set_size(self, size: int):
        """Painter size setter"""
        for shape_name in self.shape_painter_dict.keys():
            self.shape_painter_dict[shape_name].set_size(size)

    def get_size(self) -> int:
        """Painter size getter"""
        return self.shape_painter_dict[self.shape_name].get_size()

    def draw_shape(self, img: np.ndarray, center_position: tuple, color: tuple):
        """Draws the shape on an image"""
        try:
            self.current_shape_painter.draw_on_image(img, center_position, color)
        except KeyError as err:
            print(f'There is no shape with name {err}.')
