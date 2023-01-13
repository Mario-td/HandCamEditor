"""Deep dream model file"""
import dataclasses
import random
from typing import Dict
import os

import tensorflow as tf
import cv2
import numpy as np

from PyQt5.QtCore import pyqtSignal, QObject

from model.editing_tools import EditingToolModel


class DeepDreamActionModel(EditingToolModel):
    """Controller of the deep dream action"""
    def __init__(self, img_editor):
        super().__init__(img_editor)
        os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
        self.base_model = tf.keras.applications.InceptionV3(include_top=False,
                                                            weights='imagenet')
        self.signal_sender = SignalSender()
        self.deep_dream_layers: Dict[str, list] = \
            {'Curly': ['mixed0'],
             'Stripes': ['mixed1'],
             'Shapes': ['mixed2'],
             'Holes': ['mixed3'],
             'Random': ['mixed5', 'mixed6', 'mixed7', 'mixed9']}
        self.resized_original_img = None

    def resize_original_image(self):
        """Downsizing the image makes it easier to work with"""
        self.resized_original_img = \
            ImageProcessing.resize_img(self.image_editor.get_current_image(),
                                       max_dim=500)

    def apply_dream(self, dream_name: str):
        """Apply dream method"""
        # Maximize the activations of these layers
        layers = self.select_layers(dream_name)

        # Create the feature extraction model
        dream_model = tf.keras.Model(inputs=self.base_model.input, outputs=layers)

        deep_dream = DeepDream(dream_model)
        dream_img = deep_dream.run(img=self.resized_original_img,
                                   steps=40, step_size=0.02)
        size = self.image_editor.get_current_image_size()
        dream_img = cv2.resize(np.array(dream_img),
                               (size[1], size[0]),
                               interpolation=cv2.INTER_AREA)

        self.image_editor.tmp_img = dream_img
        self.signal_sender.deep_dream_finished.emit()

    def select_layers(self, dream_name: str) -> list:
        """Model layers selector"""
        layers: list = self.deep_dream_layers[dream_name]
        if dream_name == 'Random':
            chosen_layers: int = random.randint(0, len(layers) - 1)
            return [self.base_model.get_layer(layers[chosen_layers]).output]

        return [self.base_model.get_layer(layer).output for layer in layers]


@dataclasses.dataclass
class SignalSender(QObject):
    """Class for sending signals of the deep dream"""
    def __init__(self):
        super(QObject, self).__init__()

    deep_dream_finished = pyqtSignal()


class ImageProcessing:
    """Class that contains useful methods used in the deep dream model"""
    @staticmethod
    def resize_img(img, max_dim=None):
        """Resize an image"""
        if max_dim:
            img = cv2.resize(img, (max_dim, max_dim), interpolation=cv2.INTER_AREA)
        return img

    @staticmethod
    def deprocess(img):
        """Normalize an image"""
        img = 255 * (img + 1.0) / 2.0
        return tf.cast(img, tf.uint8)


class DeepDream(tf.Module):
    """Deep dream model class"""
    def __init__(self, model):
        super().__init__()
        self.model = model

    @tf.function(
        input_signature=(
                tf.TensorSpec(shape=[None, None, 3], dtype=tf.float32),
                tf.TensorSpec(shape=[], dtype=tf.int32),
                tf.TensorSpec(shape=[], dtype=tf.float32),)
    )
    def __call__(self, img, steps, step_size):
        for _ in tf.range(steps):
            with tf.GradientTape() as tape:
                # This needs gradients relative to `img`
                # `GradientTape` only watches `tf.Variable`s by default
                tape.watch(img)
                loss = self.calc_loss(img, self.model)

            # Calculate the gradient of the loss with respect to the pixels of the input image.
            gradients = tape.gradient(loss, img)

            # Normalize the gradients.
            gradients /= tf.math.reduce_std(gradients) + 1e-8

            img = img + gradients * step_size
            img = tf.clip_by_value(img, -1, 1)

        return img

    def run(self, img, steps=100, step_size=0.01):
        """Runs the model"""
        img = tf.keras.applications.inception_v3.preprocess_input(img)
        img = tf.convert_to_tensor(img)
        step_size = tf.convert_to_tensor(step_size)
        steps_remaining = steps
        step = 0
        while steps_remaining:
            if steps_remaining > 100:
                run_steps = tf.constant(100)
            else:
                run_steps = tf.constant(steps_remaining)
            steps_remaining -= run_steps
            step += run_steps

            img = self(img[:, :, :3], run_steps, tf.constant(step_size))

        result = ImageProcessing.deprocess(img)

        return result

    @staticmethod
    def calc_loss(img, model):
        """Loss calculator"""

        # Pass forward the image through the model to retrieve the activations.
        # Converts the image into a batch of size 1.
        img_batch = tf.expand_dims(img, axis=0)
        layer_activations = model(img_batch)
        if len(layer_activations) == 1:
            layer_activations = [layer_activations]

        losses = []
        for act in layer_activations:
            loss = tf.math.reduce_mean(act)
            losses.append(loss)

        return tf.reduce_sum(losses)
