"""Main window GUI for the game.

PyQt required.

  Example:
    app = QApplication([])
    board = majiang.Board(pmn_file)
    game = majiang.graphics.game.GameWindow(board)
    sys.exit(app.exec())
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMainWindow, QWidget, QApplication, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QTableWidget, QTableWidgetItem

from majiang.consts import *
from majiang.graphics.tile import TileWidget
from majiang.graphics.tile_field import *

class BoardWidget(QWidget):
    """Game board widget.
    """

    def __init__(self, board):
        super().__init__()

        ptile = []
        for i in range(4):
            ptile_field = board.game_tile_manager.private_tile[i]
            tile_nums = ptile_field.to_tile_str_list()
            if ptile_field.taken_tile is None:
                taken_tile_num = None
            else:
                taken_tile_num = ptile_field.taken_tile
            ptile.append(PrivateTileWidget(tile_nums, taken_tile_num, i))

        mtile = []
        for i in range(4):
            mtile_field = board.game_tile_manager.meld_tile[i]
            meld_tile_list = []
            for m in mtile_field:
                tile_num = m.ordered_tiles
                meld_tile_single = MeldTileWidgetSingle(tile_num, i, m.meld_idx)
                meld_tile_list.append(meld_tile_single)
            mtile.append(MeldTileWidget(meld_tile_list, i))

        dtile = []
        for i in range(4):
            dtile_field = board.game_tile_manager.discard_tile[i]
            tile_num = dtile_field.ordered_tiles
            dtile.append(DiscardTileWidget(tile_num, i))

        center_panel = QWidget()
        center_panel.setStyleSheet('background-color: black;')
        center_panel_layout = QGridLayout()
        starting = board.get_starting()
        starting_labels = []
        for seat in SEATS:
            label = QLabel('{}  {}'.format(STR_ZH['SEAT'][seat], str(starting[seat])))
            label.setStyleSheet('color: #ffffff; font-size: 16px; font-weight: bold;') 
            starting_labels.append(label)
        center_panel_layout.addWidget(starting_labels[2], 0, 1, Qt.AlignmentFlag.AlignHCenter)
        center_panel_layout.addWidget(starting_labels[3], 1, 0, Qt.AlignmentFlag.AlignHCenter)
        center_panel_layout.addWidget(starting_labels[0], 1, 2, Qt.AlignmentFlag.AlignHCenter)
        center_panel_layout.addWidget(starting_labels[1], 2, 1, Qt.AlignmentFlag.AlignHCenter)
        center_panel.setLayout(center_panel_layout)

        center_area_layout = QGridLayout()
        center_area_layout.addWidget(dtile[2], 0, 1)
        center_area_layout.addWidget(dtile[3], 1, 0)
        center_area_layout.addWidget(center_panel, 1, 1)
        center_area_layout.addWidget(dtile[1], 1, 2)
        center_area_layout.addWidget(dtile[0], 2, 1)
        minimum_size = 4 * TileWidget.size_normal[1] + 12
        center_area_layout.setRowMinimumHeight(0, minimum_size)
        center_area_layout.setRowMinimumHeight(1, minimum_size)
        center_area_layout.setRowMinimumHeight(2, minimum_size)
        center_area_layout.setColumnMinimumWidth(0, minimum_size)
        center_area_layout.setColumnMinimumWidth(1, minimum_size)
        center_area_layout.setColumnMinimumWidth(2, minimum_size)
        center_area_layout.setContentsMargins(0, 0, 0, 0)
        center_area_layout.setSpacing(0)
        center_area = QWidget()
        center_area.setLayout(center_area_layout)

        taken_tile_widgets = []
        for position in POSITIONS:
            ptile_field = board.game_tile_manager.private_tile[position]
            if ptile_field.taken_tile is None:
                taken_tile_widgets.append(QWidget())
            else:
                taken_tile_widgets.append(TileWidget(ptile_field.taken_tile, position))

        whole_layout = QGridLayout()
        whole_layout.addWidget(ptile[2], 0, 1, 1, 3, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        whole_layout.addWidget(mtile[2], 1, 0, 1, 5, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        whole_layout.addWidget(ptile[3], 2, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        whole_layout.addWidget(mtile[3], 2, 1, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        whole_layout.addWidget(center_area, 2, 2)
        whole_layout.addWidget(mtile[1], 2, 3, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        whole_layout.addWidget(ptile[1], 2, 4, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        whole_layout.addWidget(mtile[0], 3, 0, 1, 5, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        whole_layout.addWidget(ptile[0], 4, 0, 1, 5, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        whole_layout.setRowMinimumHeight(0, TileWidget.size_normal[1])
        whole_layout.setRowMinimumHeight(1, TileWidget.size_normal[1])
        whole_layout.setRowMinimumHeight(2, TileWidget.size_normal[0])
        whole_layout.setRowMinimumHeight(3, TileWidget.size_normal[1])
        whole_layout.setRowMinimumHeight(4, TileWidget.size_normal[1])
        whole_layout.setColumnMinimumWidth(0, TileWidget.size_normal[1])
        whole_layout.setColumnMinimumWidth(1, TileWidget.size_normal[1])
        whole_layout.setColumnMinimumWidth(2, TileWidget.size_normal[0])
        whole_layout.setColumnMinimumWidth(3, TileWidget.size_normal[1])
        whole_layout.setColumnMinimumWidth(4, TileWidget.size_normal[1])
        whole_layout.setContentsMargins(0, 0, 0, 0)
        whole_layout.setSpacing(0)
        game_area = QWidget()
        game_area.setLayout(whole_layout)
        # game_area.setStyleSheet('background-color: #18978f;')
        game_area.setStyleSheet('background-color: #003366;')

        button_layout = QGridLayout()
        button_layout.addWidget(QPushButton('<'), 0, 0)
        button_layout.addWidget(QPushButton('>'), 0, 1)
        button_layout.addWidget(QPushButton('<<'), 1, 0)
        button_layout.addWidget(QPushButton('>>'), 1, 1)
        button_layout.addWidget(QPushButton('<<<'), 2, 0)
        button_layout.addWidget(QPushButton('>>>'), 2, 1)
        button_area = QWidget()
        button_area.setLayout(button_layout)

        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(game_area, 0, 0)
        # TODO: implement
        # layout.addWidget(button_area, 0, 1)
        # layout.addWidget(graph_area, 1, 0, 1, 2)
        self.setLayout(layout)

class ResultDialog(QDialog):
    """Result dialog widget.
    """

    def __init__(self, parent):
        super().__init__(parent)
        fans = parent.board.get_fan()
        hu_tile = None
        for player in SEATS:
            taken_tile = parent.board.game_tile_manager.private_tile[player].taken_tile
            if taken_tile is not None:
                hu_tile = taken_tile
                break

        if hu_tile is None:
            hu_tile = parent.board.get_discarded_tile()

        self.setStyleSheet('background: #c5c5c5; color: #000000; font-size: 16px;')
        self.setWindowOpacity(0.93);

        result_desc_layout = QGridLayout()
        result_desc_widget = QWidget()
        starting = parent.board.get_starting()
        result = parent.board.get_result()
        penalty = parent.board.get_penalty()
        has_penalty = False
        for seat in SEATS:
            if penalty[seat] != 0:
                has_penalty = True
                break
        starting_labels = []
        result_labels = []
        penalty_labels = []
        total_labels = []
        for seat in SEATS:
            starting_labels.append(QLabel(str(starting[seat])))
            result_labels.append(QLabel(str(result[seat])))
            penalty_labels.append(QLabel(str(penalty[seat])))
            total_labels.append(QLabel(str(starting[seat] + result[seat] + penalty[seat])))
        for seat in SEATS:
            starting_labels[seat].setStyleSheet('color: #000000;')
            self.__set_score_label_css(result_labels[seat], result[seat])
            self.__set_score_label_css(penalty_labels[seat], penalty[seat])
            self.__set_score_label_css(total_labels[seat], penalty[seat])
            total_labels[seat].setStyleSheet('font-weight: bold;')

        result_desc_layout.addWidget(starting_labels[2], 0, 2, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(result_labels[2], 1, 2, Qt.AlignmentFlag.AlignRight)
        if has_penalty:
            result_desc_layout.addWidget(penalty_labels[2], 2, 2, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(total_labels[2], 3, 2, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(starting_labels[3], 4, 1, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(result_labels[3], 5, 1, Qt.AlignmentFlag.AlignRight)
        if has_penalty:
            result_desc_layout.addWidget(penalty_labels[3], 6, 1, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(total_labels[3], 7, 1, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(starting_labels[1], 4, 3, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(result_labels[1], 5, 3, Qt.AlignmentFlag.AlignRight)
        if has_penalty:
            result_desc_layout.addWidget(penalty_labels[1], 6, 3, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(total_labels[1], 7, 3, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(starting_labels[0], 8, 2, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(result_labels[0], 9, 2, Qt.AlignmentFlag.AlignRight)
        if has_penalty:
            result_desc_layout.addWidget(penalty_labels[0], 10, 2, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.addWidget(total_labels[0], 11, 2, Qt.AlignmentFlag.AlignRight)
        result_desc_layout.setHorizontalSpacing(100)
        result_desc_layout.setColumnMinimumWidth(0, 100)
        result_desc_layout.setColumnMinimumWidth(4, 100)
        result_desc_widget.setLayout(result_desc_layout)

        layout_idx = 0
        dialog_layout = QGridLayout()
        dialog_layout.addWidget(result_desc_widget, layout_idx, 0, 1, 5)
        layout_idx += 1

        for player_idx, fan in enumerate(fans):
            if len(fan) == 0:
                continue

            mtile_field = parent.board.game_tile_manager.meld_tile[player_idx]
            meld_tile_list = []
            for m in mtile_field:
                tile_num = m.ordered_tiles
                meld_tile_single = MeldTileWidgetSingle(tile_num, DOWN, m.meld_idx)
                meld_tile_list.append(meld_tile_single)
            mtile_ = MeldTileWidget(meld_tile_list, DOWN)

            ptile_field = parent.board.game_tile_manager.private_tile[player_idx]
            tile_nums = ptile_field.to_tile_str_list()
            if hu_tile is not None:
                taken_tile_num = hu_tile
            ptile_ = PrivateTileWidget(tile_nums, taken_tile_num, DOWN)

            dialog_layout.addWidget(mtile_, layout_idx, 0, 1, 5, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            layout_idx += 1
            dialog_layout.addWidget(ptile_, layout_idx, 0, 1, 5, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
            layout_idx += 1
            total_point = 0
            for _, (fan_no, fan_num) in enumerate(fan):
                point = FANZHONG_POINT[fan_no - 1] * fan_num
                dialog_layout.addWidget(QLabel(FAN_NAME_ZH[fan_no - 1]), layout_idx, 1, Qt.AlignmentFlag.AlignLeft)
                dialog_layout.addWidget(QLabel('{} * {} = {}'.format(FANZHONG_POINT[fan_no - 1], fan_num, point)), layout_idx, 3, Qt.AlignmentFlag.AlignRight)
                total_point += point
                layout_idx += 1
            total_point_str_label = QLabel(STR_ZH['TOTAL_POINT'])
            total_point_str_label.setStyleSheet('font-weight: bold;')
            total_point_label = QLabel(str(total_point))
            total_point_label.setStyleSheet('font-weight: bold;')
            dialog_layout.addWidget(total_point_str_label, layout_idx, 1, Qt.AlignmentFlag.AlignLeft)
            dialog_layout.addWidget(total_point_label, layout_idx, 3, Qt.AlignmentFlag.AlignRight)
            layout_idx += 1
        self.setLayout(dialog_layout)

    def __set_score_label_css(self, label, score_num):
        """Set CSS of score labels according to the score number.

        Args:
            label (QLabel): score label
            score_num (int): score
        """
        if score_num > 0:
            label.setStyleSheet('color: #00ffff')
        elif score_num == 0:
            label.setStyleSheet('color: #000000')
        else:
            label.setStyleSheet('color: #ff0000')

class GameWindow(QMainWindow):
    """Game window.

    Attribures:
        board (majiang.Board): game board
        board_widget (majiang.graphics.BoardWidget): game board widget
    """

    def __init__(self, board):
        super().__init__()

        self.board = board
        self.init_ui()
        self.show()
        center_x = (QApplication.instance().screens()[0].size().width() - self.width()) / 2
        center_y = (QApplication.instance().screens()[0].size().height() - self.height()) / 2
        self.move(center_x, center_y)

    def init_ui(self):
        """Initialize UI.
        """

        self.setWindowTitle('Majiang')
        self.board_widget = BoardWidget(self.board)
        self.setCentralWidget(self.board_widget)

    def keyPressEvent(self, e):
        """Set keyPressEvent.

        Esc: exit
        Right: next_action
        Left: prev_action
        Down: to the last action
        Up: to the first action
        """
        gw = self.board_widget
        if e.key() == Qt.Key.Key_Escape.value:
            self.close()

        if e.key() == Qt.Key.Key_Right.value:
            self.board.next_action(1)
            self.init_ui()
            if self.board.is_end():
                self.result_dialog = ResultDialog(self)
                self.result_dialog.exec()

        if e.key() == Qt.Key.Key_Left.value:
            self.board.prev_action(1)
            self.init_ui()

        if e.key() == Qt.Key.Key_Down.value:
            self.board.to_last_action()
            self.init_ui()
            if self.board.is_end():
                self.result_dialog = ResultDialog(self)
                self.result_dialog.exec()

        if e.key() == Qt.Key.Key_Up.value:
            self.board.to_first_action()
            self.init_ui()
            if self.board.is_end():
                self.result_dialog = ResultDialog(self)
                self.result_dialog.exec()
