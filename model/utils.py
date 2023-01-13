"""Utils file"""
from PyQt5.QtGui import QImage, QPixmap

import numpy as np


def image_to_pixmap(img: np.ndarray) -> QPixmap:
    """Gets an numpy array and returns a pixmap"""
    q_pixmap = QPixmap.fromImage(QImage(img.data, img.shape[1],
                                        img.shape[0],
                                        img.shape[2] * img.shape[1],
                                        QImage.Format_BGR888))
    return q_pixmap
