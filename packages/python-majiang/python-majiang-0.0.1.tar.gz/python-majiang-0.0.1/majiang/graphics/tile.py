"""Majiang tile GUI widget.

PyQt required.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QLabel, QGridLayout
from PyQt6.QtGui import QPixmap

from majiang.consts import *

class TileWidget(QWidget):
    """Majiang tile GUI widget.
    """

    size_normal = (36, 54)
    def __init__(self, number, position):
        super().__init__()

        img_path = '/home/zuo/WorkSpace/python-majiang/resources/img/tile/{}/{}.png'.format(position, number)
        width = TileWidget.size_normal[0]
        height = TileWidget.size_normal[1]
        if position in [RIGHT, LEFT]:
            width = TileWidget.size_normal[1]
            height = TileWidget.size_normal[0]
        pix = QPixmap(img_path).scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        tile_label = QLabel(self)
        tile_label.setPixmap(pix)
        tile_label.setStyleSheet('background: white; border: 1px solid; border-radius: 3px;')

        layout = QGridLayout()
        layout.addWidget(tile_label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
