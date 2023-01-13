"""Resize model file"""
import cv2

from .editing_tool import EditingToolModel


class ResizeActionModel(EditingToolModel):
    """Controller of the resize action"""

    def change_temp_image_width(self, width: int):
        """Change the temporary image width"""
        self.image_editor.tmp_img = cv2.resize(self.image_editor.get_current_image(),
                                               (width, self.image_editor.tmp_img.shape[0]),
                                               cv2.INTER_AREA)

    def change_temp_image_height(self, height: int):
        """Change the temporary image height"""
        self.image_editor.tmp_img = cv2.resize(self.image_editor.get_current_image(),
                                               (self.image_editor.tmp_img.shape[1], height),
                                               cv2.INTER_AREA)

    def get_size_with_ratio(self, width: int = None, height: int = None):
        """Current image size with ratio getter"""
        current_height, current_width = self.image_editor.get_current_image_size()
        if not width:
            width = int(current_width * height / current_height)

        if not height:
            height = int(current_height * width / current_width)

        return width, height
