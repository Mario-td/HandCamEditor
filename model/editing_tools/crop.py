"""Crop model file"""
from .editing_tool import EditingToolModel


class CropActionModel(EditingToolModel):
    """Controller of the cropping action"""

    def crop_image(self, origin_x: int, origin_y: int, width: int, height: int):
        """Crops the temporary image"""
        self.image_editor.tmp_img =\
            self.image_editor.tmp_img[origin_y:origin_y + height, origin_x:origin_x + width].copy()
