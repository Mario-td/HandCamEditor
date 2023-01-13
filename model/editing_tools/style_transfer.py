"""Style transfer model file"""
import dataclasses
import glob
import ntpath
import shutil
import os

import cv2
import numpy as np
import tensorflow as tf
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap

from model.editing_tools import EditingToolModel
from model.utils import image_to_pixmap

STYLE_IMAGES_PATH = 'model/style_images'
ML_MODEL_PATH = './model/ML_models/magenta_arbitrary-image-stylization-v1-256_2'
TMP_PATH = './model/style_images/tmp'


class StyleTransferActionModel(EditingToolModel):
    """Controller of the style transfer action"""

    def __init__(self, img_editor):
        super().__init__(img_editor)
        self.styled_images_directories = []
        self.styled_images = {}
        self.styled_images_pixmap = {}
        self.load_styled_images_directory()
        self.style_transfer_executor = StyleTransferExecutor()
        self.signal_sender = SignalSender()

    def load_styled_images_directory(self):
        """Loads a new styled image path"""
        filenames = glob.glob(STYLE_IMAGES_PATH + '/*.jpg')
        self.styled_images_directories = filenames
        self.read_all_styled_images()

    def add_styled_image_directory(self, path: str):
        """Adds a new styled image path"""
        self.read_styled_image(path)
        self.styled_images_directories.append(path)

    @staticmethod
    def path_leaf(path):
        """Returns the file name given a path"""
        head, tail = ntpath.split(path)
        return tail or ntpath.basename(head)

    def read_styled_image(self, directory):
        """Method for reading a styled image"""
        image = cv2.imread(directory)
        name = self.path_leaf(directory)
        self.styled_images_pixmap[name] = image_to_pixmap(image)
        self.styled_images[name] = image

    def read_all_styled_images(self):
        """Method for reading all the styled images"""
        for directory in self.styled_images_directories:
            image = cv2.imread(directory)
            name = self.path_leaf(directory)
            self.styled_images_pixmap[name] = image_to_pixmap(image)
            self.styled_images[name] = image

    def get_all_filtered_images_pixmap(self) -> dict:
        """Filtered pixmap getter"""
        return self.styled_images_pixmap

    def get_filter_image_pixmap(self, name) -> QPixmap:
        """Filtered image pixmap getter"""
        return self.styled_images_pixmap[name]

    def apply_style_transfer(self, style_name: str, image: np.ndarray) -> None:
        """Apply style transfer"""
        self.style_transfer_executor.\
            apply_style_transfer(self.styled_images[style_name], image)
        self.image_editor.tmp_img = self.style_transfer_executor.stylized_image
        self.signal_sender.style_transfer_finished.emit()


@dataclasses.dataclass
class SignalSender(QObject):
    """Signal sender for the style transfer class"""
    def __init__(self):
        super(QObject, self).__init__()

    style_transfer_finished = pyqtSignal()


class StyleTransferExecutor:
    """Class for executing the style transfer"""
    def __init__(self):
        self.stylized_image = None
        self.ml_model = tf.saved_model.load(ML_MODEL_PATH)
        self.content_image_path = TMP_PATH + '/content_image.jpg'
        self.style_image_path = TMP_PATH + '/style_image.jpg'

    @staticmethod
    def scale_image(img, max_dim=512):
        """Scales the image"""
        original_shape = tf.cast(tf.shape(img)[:-1], tf.float32)
        scale_ratio = max_dim / max(original_shape)

        new_shape = tf.cast(original_shape * scale_ratio, tf.int32)

        return tf.image.resize(img, new_shape)

    def load_img(self, path_to_img):
        """Loads an image given a path"""
        img = tf.io.read_file(path_to_img)
        img = tf.image.decode_image(img, channels=3)
        img = tf.image.convert_image_dtype(img, tf.float32)
        img = self.scale_image(img)

        return img[tf.newaxis, :]

    def apply_style_transfer(self, style_image: np.ndarray, content_image: np.ndarray):
        """Method for applying style transfer"""
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH)

        cv2.imwrite(self.content_image_path, content_image)
        cv2.imwrite(self.style_image_path, style_image)

        size = content_image.shape

        content_image = self.load_img(self.content_image_path)
        style_image = self.load_img(self.style_image_path)

        try:
            shutil.rmtree(TMP_PATH)
        except OSError as error:
            print("Error: %s : %s" % (TMP_PATH, error.strerror))

        self.stylized_image = self.ml_model(tf.constant(content_image),
                                            tf.constant(style_image))[0]

        self.stylized_image = cv2.cvtColor(self.stylized_image.numpy()[0],
                                           cv2.COLOR_RGB2BGR)
        self.stylized_image = cv2.normalize(self.stylized_image,
                                            None, 0, 255, cv2.NORM_MINMAX, cv2.CV_8U)
        self.stylized_image = cv2.resize(self.stylized_image, (size[1], size[0]),
                                         cv2.INTER_AREA)
