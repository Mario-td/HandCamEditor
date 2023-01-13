"""Filter model file"""
from .editing_tool import EditingToolModel
from ..image_filter import ImageFilterContainer


class FilterActionModel(EditingToolModel):
    """Controller of the filter action"""
    def __init__(self, img_editor: 'ImageEditor'):
        super().__init__(img_editor)
        self.filter_container = None

    def filter_temp_image(self, filter_name: str):
        """Applies a filter on the temporary image"""
        self.image_editor.tmp_img = self.filter_container.get_filtered_image(filter_name)

    def set_filters(self, filter_container: ImageFilterContainer):
        """Image container setter"""
        self.filter_container = filter_container
