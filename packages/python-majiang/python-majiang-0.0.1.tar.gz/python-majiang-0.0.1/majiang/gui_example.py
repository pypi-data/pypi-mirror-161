import sys

from PyQt6.QtWidgets import QApplication

from majiang import *
from majiang.graphics import *

if __name__ == '__main__':
    pmn_file = 'tests/pmn_files/example_2.pmn'
    app = QApplication([])
    board = Board(pmn_file)
    game = GameWindow(board)
    sys.exit(app.exec())
