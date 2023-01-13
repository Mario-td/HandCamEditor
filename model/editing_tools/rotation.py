"""Rotation model file"""
import cv2

from .editing_tool import EditingToolModel


class RotationActionModel(EditingToolModel):
    """Controller of the rotation action"""

    def rotate_temp_image(self, action_text: str):
        """Rotates the temporary image"""
        if action_text == "V":
            self.image_editor.tmp_img = cv2.flip(self.image_editor.tmp_img, 0)
        elif action_text == "H":
            self.image_editor.tmp_img = cv2.flip(self.image_editor.tmp_img, 1)
        elif action_text == "L":
            self.image_editor.tmp_img = cv2.rotate(self.image_editor.tmp_img,
                                                   cv2.ROTATE_90_COUNTERCLOCKWISE)
        elif action_text == "R":
            self.image_editor.tmp_img = cv2.rotate(self.image_editor.tmp_img,
                                                   cv2.ROTATE_90_CLOCKWISE)
