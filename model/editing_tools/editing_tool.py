"""Editing tool model module"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from model import ImageEditor


class EditingToolModel:
    """Controller of the cropping action"""
    def __init__(self, img_editor: 'ImageEditor'):
        self.image_editor = img_editor
