"""Adjust model file"""
import dataclasses
from abc import ABC, abstractmethod
from typing import Optional

from PIL import Image, ImageEnhance
import cv2
import numpy as np
from mypy_extensions import TypedDict

from model.editing_tools import EditingToolModel

SLIDER_MAX_VALUE = 100


class AdjustActionModel(EditingToolModel):
    """Controller of the adjust action"""

    def __init__(self, img_editor):
        super().__init__(img_editor)

        self.image_before_editing: np.ndarray = np.zeros((1, 1, 3), np.uint8)
        self.current_edited_image: np.ndarray = np.zeros((1, 1, 3), np.uint8)
        self.image_before_current_feature_applies: np.ndarray = np.zeros((1, 1, 3), np.uint8)

        self.feature_container = FeatureContainer()
        self.feature_container.append_feature('Brightness', Brightness())
        self.feature_container.append_feature('Contrast', Contrast())
        self.feature_container.append_feature('Saturation', Saturation())
        self.feature_container.append_feature('Sharpness', Sharpness())

    def initialize_features(self):
        """Initializes all the feature changers"""
        self.feature_container.set_all_to_zero()
        self.image_before_editing = self.image_editor.get_current_image().copy()
        self.current_edited_image = self.image_editor.get_current_image().copy()

    def get_feature_value(self) -> int:
        """Feature changer value getter"""
        return self.feature_container.current_feature.get_value()

    def change_value(self, value: int):
        """Changes the value of the current feature changer and it applies it to the image"""
        self.feature_container.change_current_feature_value(value)
        self.current_edited_image = \
            self.feature_container.apply_all_feature_changes(self.image_before_editing.copy())
        self.image_editor.tmp_img = self.current_edited_image

    def set_feature(self, feature_name):
        """Feature changer value setter"""
        self.feature_container.set_feature(feature_name)
        self.image_before_current_feature_applies = \
            self.feature_container.apply_all_feature_changes(self.image_before_editing.copy())


@dataclasses.dataclass
class FeatureStrategy(ABC):
    """Feature changer. Strategy pattern"""
    value: int = 0

    def set_value(self, value: int):
        """Value setter"""
        self.value = value

    def get_value(self) -> int:
        """Value getter"""
        return self.value

    @abstractmethod
    def change_image_feature(self, img: np.array) -> np.ndarray:
        """Changes the intensity of the feature that is being changed"""


class Brightness(FeatureStrategy):
    """Brightness changer"""
    def change_image_feature(self, img: np.array):
        if self.value != 0:
            img = cv2.add(img, (int(self.value * 2.55), int(self.value * 2.55),
                                int(self.value * 2.55), 0))
        return img


class Contrast(FeatureStrategy):
    """Contrast changer"""
    def change_image_feature(self, img: np.array):
        contrast = self.value / 2
        if contrast != 0:
            alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast))
            gamma = 127 * (1 - alpha)

            img = cv2.addWeighted(img, alpha,
                                  img, 0, gamma)

        return img


class Saturation(FeatureStrategy):
    """Saturation changer"""
    def change_image_feature(self, img: np.array):
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        enhancer = ImageEnhance.Color(pil_img)
        pil_img = enhancer.enhance((self.value + SLIDER_MAX_VALUE) / SLIDER_MAX_VALUE)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return img


class Sharpness(FeatureStrategy):
    """Sharpness changer"""
    def change_image_feature(self, img: np.array):
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        enhancer = ImageEnhance.Sharpness(pil_img)
        pil_img = enhancer.enhance((self.value + SLIDER_MAX_VALUE) * 2 / SLIDER_MAX_VALUE)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        return img


class FeatureDict(TypedDict):
    """Feature dictionary"""
    name: str
    feature: FeatureStrategy


@dataclasses.dataclass
class FeatureContainer:
    """Container of all the feature classes"""
    feature_container_dict = FeatureDict()
    current_feature: Optional[FeatureStrategy] = None

    def set_all_to_zero(self):
        """Set all the features value at zero"""
        for feature in self.feature_container_dict.values():
            feature.set_value(0)

    def append_feature(self, feature_name: str, feature: FeatureStrategy):
        """Appends a new feature"""
        self.feature_container_dict[feature_name] = feature

    def set_feature(self, feature_name: str):
        """Sets the current feature"""
        self.current_feature = self.feature_container_dict[feature_name]

    def apply_feature_change(self, img: np.ndarray) -> np.ndarray:
        """Applies a change of the current feature"""
        try:
            return self.current_feature.change_image_feature(img)
        except KeyError as err:
            print(f'There is no feature with name {err}.')
            return np.zeros((1, 1, 3), np.uint8)

    def apply_all_feature_changes(self, img: np.ndarray) -> np.ndarray:
        """All the feature changes will be applied"""
        for _, feature in self.feature_container_dict.items():
            img = feature.change_image_feature(img)
        return img

    def change_current_feature_value(self, value: int):
        """Changes the value of the current value"""
        self.current_feature.set_value(value)
