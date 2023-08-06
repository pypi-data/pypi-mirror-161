"""Majiang tile field GUI widget.

PyQt required.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QHBoxLayout

from majiang.consts import *
from majiang.graphics.tile import TileWidget

class PrivateTileWidget(QWidget):
    """One player's all private tile widget.
    """

    def __init__(self, tile_nums, taken_tile, position):
        super().__init__()

        margin = 17
        if taken_tile:
            taken_tile_widget = TileWidget(taken_tile, position)
        else:
            taken_tile_widget = QWidget()
        dummy_widget = QWidget()
        if position == DOWN:
            layout = QHBoxLayout()
            layout.setContentsMargins(0, margin, 0, 0)
            dummy_widget.setMinimumWidth(TileWidget.size_normal[0] * 1.5)
            layout.addWidget(dummy_widget)
            for t in tile_nums:
                layout.addWidget(TileWidget(t, position))
            taken_tile_widget.setMinimumWidth(TileWidget.size_normal[0] * 1.5 + 1)
            taken_tile_widget.setStyleSheet('margin-left: {}px;'.format(TileWidget.size_normal[0] * 0.5))
            layout.addWidget(taken_tile_widget)
        elif position == RIGHT:
            layout = QVBoxLayout()
            layout.setContentsMargins(margin, 0, 0, 0)
            taken_tile_widget.setMinimumHeight(TileWidget.size_normal[0] * 1.5 + 1)
            layout.addWidget(taken_tile_widget)
            for t in reversed(tile_nums):
                layout.addWidget(TileWidget(t, position))
            dummy_widget.setMinimumHeight(TileWidget.size_normal[0] * 1.5)
            layout.addWidget(dummy_widget)
        elif position == UP:
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, margin)
            taken_tile_widget.setMinimumWidth(TileWidget.size_normal[0] * 1.5 + 1)
            layout.addWidget(taken_tile_widget)
            for t in reversed(tile_nums):
                layout.addWidget(TileWidget(t, position))
            dummy_widget.setMinimumWidth(TileWidget.size_normal[0] * 1.5)
            layout.addWidget(dummy_widget)
        elif position == LEFT:
            layout = QVBoxLayout()
            layout.setContentsMargins(0, 0, margin, 0)
            dummy_widget.setMinimumHeight(TileWidget.size_normal[0] * 1.5)
            layout.addWidget(dummy_widget)
            taken_tile_widget.setMinimumHeight(TileWidget.size_normal[0] * 1.5 + 1)
            for t in tile_nums:
                layout.addWidget(TileWidget(t, position))
            layout.addWidget(taken_tile_widget)
        else:
            raise ValueError('Position {} is invalid'.format(position))

        layout.setSpacing(0)
        self.setLayout(layout)

class MeldTileWidgetSingle(QWidget):
    """Single group of melded tile widget.
    """

    def __init__(self, tile_nums, position, meld_idx):
        super().__init__()

        if position == DOWN:
            layout = QHBoxLayout()
            for idx, t in enumerate(tile_nums):
                if meld_idx is not None and idx == meld_idx:
                    layout.addWidget(TileWidget(t, (position + 1) % len(POSITIONS)))
                else:
                    layout.addWidget(TileWidget(t, position))
            layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        elif position == RIGHT:
            layout = QVBoxLayout()
            for idx, t in enumerate(reversed(tile_nums)):
                if meld_idx is not None and idx == len(tile_nums) - 1 - meld_idx:
                    layout.addWidget(TileWidget(t, (position + 1) % len(POSITIONS)))
                else:
                    layout.addWidget(TileWidget(t, position))
        elif position == UP:
            layout = QHBoxLayout()
            for idx, t in enumerate(reversed(tile_nums)):
                if meld_idx is not None and idx == len(tile_nums) - 1 - meld_idx:
                    layout.addWidget(TileWidget(t, (position + 1) % len(POSITIONS)))
                else:
                    layout.addWidget(TileWidget(t, position))
        elif position == LEFT:
            layout = QVBoxLayout()
            for idx, t in enumerate(tile_nums):
                if meld_idx is not None and idx == meld_idx:
                    layout.addWidget(TileWidget(t, (position + 1) % len(POSITIONS)))
                else:
                    layout.addWidget(TileWidget(t, position))
        else:
            raise ValueError('Position {} is invalid'.format(position))

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

class MeldTileWidget(QWidget):
    """One player's all melded tile widget.
    """

    def __init__(self, meld_tile_singles, position):
        super().__init__()

        if position == DOWN:
            layout = QHBoxLayout()
            for mt in meld_tile_singles:
                layout.addWidget(mt)
        elif position == RIGHT:
            layout = QVBoxLayout()
            for mt in reversed(meld_tile_singles):
                layout.addWidget(mt)
        elif position == UP:
            layout = QHBoxLayout()
            for mt in reversed(meld_tile_singles):
                layout.addWidget(mt)
        elif position == LEFT:
            layout = QVBoxLayout()
            for mt in meld_tile_singles:
                layout.addWidget(mt)
        else:
            raise ValueError('Position {} is invalid'.format(position))

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

class DiscardTileWidget(QWidget):
    """One player's all discarded tile widget.
    """

    def __init__(self, tile_nums, position):
        super().__init__()

        lines_total = len(tile_nums) // 6 + 1
        layout = QGridLayout()
        if position == DOWN:
            for idx, t in enumerate(tile_nums):
                layout.addWidget(TileWidget(t, position), idx // 6, idx % 6)
                layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        elif position == RIGHT:
            for idx, t in enumerate(tile_nums):
                layout.addWidget(TileWidget(t, position), 5 - idx % 6, idx // 6)
                layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        elif position == UP:
            for idx, t in enumerate(tile_nums):
                layout.addWidget(TileWidget(t, position), lines_total - 1 - idx // 6, 5 - idx % 6)
                layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        elif position == LEFT:
            for idx, t in enumerate(tile_nums):
                layout.addWidget(TileWidget(t, position), idx % 6, lines_total - 1 - idx // 6)
                layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
