"""Game board.
"""

import re
from datetime import datetime

from majiang.tile import *
from majiang.tile_field import *
from majiang.game_tile_manager import *
from majiang.consts import *

class Board(object):
    """Game board to represent all information of the game.

    Attributes:
        pmn_dict (dict): dict for saving pmn file info
        game_tile_manager (majiang.GameTileManager): to manage tiles in the game
        play_log (list of str): playing log
        play_current_idx (int): current index of play_log
        win_from (int): win from the wall(0) or other player(1)
        win_from_player (int): the play to win from. None for winning from the wall
    """

    def __init__(self, pmn_file_path, step=0):
        """

        Args:
            pmn_file_path: PMN file path
        """

        self.pmn_dict = {}
        self.game_tile_manager = GameTileManager()
        self.__set_pmn(pmn_file_path)
        self.play_current_idx = 0
        self.win_from = None
        self.win_from_player = None
        self.next_action(step)

    def __set_pmn(self, pmn_file_path):
        """Parses a PMN file and sets information to pmn_dict.

        Args:
            pmn_file_path: PMN file path

        Raises:
            ValueError: invalid pmn string
        """

        with open(pmn_file_path, mode='r') as f:
            err_msgs = []

            for line in f.readlines():
                line = line.strip("\r\n")
                k, v = self.__split_notation_line(line)
                self.pmn_dict[k] = v

            required_keys = [
                'Event', 'Site', 'Date', 'Board', 'PWind', 'East', 'South', 'West', 'North', 'Deal', 'Scoring',
                'Starting', 'Result', 'Penalty', 'Play', 'Fan'
            ]
            for k in required_keys:
                if k not in self.pmn_dict:
                    raise ValueError('PMN string should contains {} key'.format(k))

            try:
                y, m, d = [int(_) for _ in self.pmn_dict['Date'].split('.')]
                datetime(y, m, d)
            except ValueError:
                err_msgs.append('Date is not valid')

            try:
                _ = int(self.pmn_dict['Board'])
            except ValueError:
                err_msgs.append('Board is not valid')

            if self.pmn_dict['PWind'] not in ['E', 'S', 'W', 'N']:
                err_msgs.append('PWind is not valid')

            if self.pmn_dict['Scoring'] not in ['Normal', 'Duplicate']:
                err_msgs.append('Scoring is not valid')

            try:
                re, rs, rw, rn = [int(_) for _ in self.pmn_dict['Result'].split(' ')]
            except ValueError:
                err_msgs.append('Result is not valid')

            try:
                pe, ps, pw, pn = [int(_) for _ in self.pmn_dict['Penalty'].split(' ')]
            except ValueError:
                err_msgs.append('Penalty is not valid')

            if len(err_msgs) == 0:
                if not self.__set_deal():
                    err_msgs.append('Deal is not valid')

            if len(err_msgs) == 0:
                if not self.__set_play_log():
                    err_msgs.append('Play is not valid')

            if len(err_msgs) != 0:
                raise ValueError(err_msgs)

            self.is_valid = True

    @staticmethod
    def __split_notation_line(line):
        """Parses a line of PMN file.

        Args:
            pmn_file_path: PMN file path

        Returns:
            (str, str): key and value
        """

        key, value, _ = line.split('"')
        key = key[1:-1]

        return key, value

    @staticmethod
    def __pmn_str_to_action(action_str):
        """Convert PMN action string to board action.

        Args:
            action_str: PMN action string

        Returns:
            int: action
        """

        if action_str == 'T':
            return TAKE
        elif action_str == 'D':
            return DISCARD
        elif action_str == 'C':
            return CHI
        elif action_str == 'P':
            return PENG
        elif action_str == 'A':
            return ANGANG
        elif action_str == 'B':
            return BUGANG
        elif action_str == 'Z':
            return ZHIGANG
        elif action_str == 'H':
            return HU
        else:
            return UNKNOWN

    def __set_deal(self):
        """Set starting hand.

        Returns:
            bool: success or failed

        Raises:
            ValueError: more than 4 tiles for the same kind
            ValueError: less than 1 tile for the same kind
        """

        deal_pattern = re.compile(r'(c\d*)(d\d*)(b\d*)(w\d*)(r\d*)(f\d*)')
        for seat, deal in enumerate(self.pmn_dict['Deal'].split(' ')):
            deal_groups = deal_pattern.match(deal)
            if not deal_groups:
                return False

            for i in range(1, 7):
                matched = deal_groups[i]
                suit, nums = matched[0], matched[1:]
                for n in nums:
                    self.game_tile_manager.init_take(seat, Tile(suit + n))

        return True

    def __set_play_log(self):
        """Set play log.

        Returns:
            bool: success or failed
        """

        play_str = self.pmn_dict['Play']
        s1, s2 = play_str.split('H', 1)
        chunk_size = 4
        p1 = [s1[i : i + chunk_size] for i in range(0, len(s1), chunk_size)]
        p2 = ['H' + s2]
        self.play_log = p1 + p2

        return True

    def get_turn(self):
        """Get player in the turn

        Return:
            int: player in the turn
        """

        if self.play_current_idx == 0:
            return None

        else:
            return int(self.play_log[self.play_current_idx - 1][1])

    def get_action(self):
        """Get action in the turn

        Return:
            int: action in the turn
        """

        if self.play_current_idx == 0:
            return None

        else:
            return self.__pmn_str_to_action(self.play_log[self.play_current_idx - 1][0])

    def get_discarded_tile(self):
        """Get discarded tile in the turn

        Return:
            Tile: discarded tile in the turn
        """

        if self.play_current_idx == 0:
            return None
        else:
            prev_log_idx = self.play_current_idx - 1
            prev_log = self.play_log[prev_log_idx]
            while prev_log[0] != 'D':
                prev_log_idx -= 1
                prev_log = self.play_log[prev_log_idx]

            if prev_log[2:] != DISCARD_TAKEN_TILE_STR:
                return Tile(prev_log[2:]) 

            prev_prev_log = self.play_log[prev_log_idx - 1]
            assert prev_prev_log[0] == 'T', 'Invalid play log, idx = {}'.format(self.play_current_idx)

            return Tile(prev_prev_log[2:])

    def is_end(self):
        """Judge whether the game is end.

        Return:
            bool: is end or not
        """

        return len(self.play_log) == self.play_current_idx

    def get_starting(self):
        """Get starting hand.

        Return:
            list of int: starting tile strings
        """

        return [int(r) for r in self.pmn_dict['Starting'].split(' ')]

    def get_result(self):
        """Get result point.

        Return:
            list of int: result point
        """

        return [int(r) for r in self.pmn_dict['Result'].split(' ')]

    def get_penalty(self):
        """Get penalty point.

        Return:
            list of int: penalty point
        """

        return [int(r) for r in self.pmn_dict['Penalty'].split(' ')]

    def get_fan(self):
        """Get winning fans.

        Return:
            list of list of (int, int): winning fans no. and num for each player.
        """

        result = []

        for _, fan in enumerate(self.pmn_dict['Fan'].split(' ')):
            result_ = []
            if fan != 'None':
                fan_groups = fan.split('.')
                for fg in fan_groups:
                    fan_no, fan_num = [int(x) for x in fg.split('/')]
                    result_.append((fan_no, fan_num))
            result.append(result_)

        return result

    def get_fan_zh(self):
        """Get winning fans.

        Return:
            list of list of (str, int): winning fans Chinese name and num for each player.
        """

        result = []

        for _, fan in enumerate(self.pmn_dict['Fan'].split(' ')):
            result_ = []
            if fan != 'None':
                fan_groups = fan.split('.')
                for fg in fan_groups:
                    fan_no, fan_num = [int(x) for x in fg.split('/')]
                    fan_name_zh = FAN_NAME_ZH[fan_no - 1]
                    result_.append((fan_name_zh, fan_num))
            result.append(result_)

        return result

    def get_deck_tile_list(self):
        """Get remained deck tiles list of string.

        Return:
            list of string: deck tiles string
        """

        return self.game_tile_manager.deck_tile.to_tile_str_list()

    def get_discard_tile_list(self, player):
        """Get player's discarded tiles list of string.

        Args:
            player (int): targer player

        Return:
            list of string: discarded tiles string
        """

        if player < 0 or player > 3 or not isinstance(player, int):
            raise ValueError('player must be an integer between 0 and {}'.format(len(SEATS)))

        return self.game_tile_manager.discard_tile[player].to_tile_str_list()

    def get_private_tile_list(self, player):
        """Get player's private tiles list of string.

        Args:
            player (int): targer player

        Return:
            list of string: private tiles string
        """

        if player < 0 or player > 3 or not isinstance(player, int):
            raise ValueError('player must be an integer between 0 and {}'.format(len(SEATS)))

        return self.game_tile_manager.private_tile[player].to_tile_str_list()

    def get_taken_tile(self, player):
        """Get player's taken tile string.

        Return:
            string: taken tile string
        """

        if player < 0 or player > 3 or not isinstance(player, int):
            raise ValueError('player must be an integer between 0 and {}'.format(len(SEATS)))

        return self.game_tile_manager.private_tile[player].taken_tile

    def get_meld_tile_list(self, player):
        """Get player's melded tiles list of string.

        Args:
            player (int): targer player

        Return:
            list of string: private tiles string
        """

        if player < 0 or player > 3 or not isinstance(player, int):
            raise ValueError('player must be an integer between 0 and {}'.format(len(SEATS)))

        result = []
        for m in self.game_tile_manager.meld_tile[player]:
            result.append(m.to_tile_str_list())

        return result

    def next_action(self, step=1):
        """Proceed a action from play_log.

        Args:
            step (int): num of step to proceed

        Raises:
            ValueError: invalid play_log string
        """

        for _ in range(step):
            if self.is_end():
                return

            log_str = self.play_log[self.play_current_idx]
            # TODO: validation
            # TODO: duplicate more than two players win
            action_str, action_player, action_tile_str = log_str[0], int(log_str[1]), log_str[2:]

            if action_str == 'T':
                if self.play_current_idx != 0:
                    if action_player != (self.get_turn() + 1) % len(SEATS):
                        raise ValueError('invalid action string {}'.format(action_str))

                self.game_tile_manager.take(action_player, Tile(action_tile_str))
            elif action_str == 'D':
                if action_player != self.get_turn():
                    raise ValueError('invalid action string {}'.format(action_str))

                if action_tile_str == DISCARD_TAKEN_TILE_STR:
                    self.game_tile_manager.discard_taken(action_player)
                else:
                    self.game_tile_manager.discard(action_player, Tile(action_tile_str))
            elif action_str == 'C':
                if action_player != (self.get_turn() + 1) % len(SEATS):
                    raise ValueError('invalid action string {}'.format(action_str))

                self.game_tile_manager.chi(action_player, self.get_discarded_tile(), Tile(action_tile_str))
            elif action_str == 'P':
                assert action_tile_str == str(self.get_discarded_tile()), 'Peng can only for the same tile'

                peng_from = self.get_turn()
                self.game_tile_manager.peng(action_player, Tile(action_tile_str), peng_from)
            elif action_str == 'A':
                self.game_tile_manager.angang(action_player, Tile(action_tile_str))
            elif action_str == 'B':
                self.game_tile_manager.bugang(action_player, Tile(action_tile_str))
            elif action_str == 'Z':
                assert action_tile_str == str(self.get_discarded_tile()), 'Zhigang can only for the same tile'

                zhigang_from = self.get_turn()
                zhigang_idx = (action_player - zhigang_from - 1 + len(SEATS)) % len(SEATS)
                if zhigang_idx == 2: # there are 4 tiles in a gang meld
                    zhigang_idx = 3
                self.game_tile_manager.zhigang(action_player, Tile(action_tile_str), zhigang_idx, zhigang_from)
            elif action_str == 'H':
                if self.get_action() == TAKE:
                    self.win_from = FROM_WALL
                    self.win_from_player = None
                else:
                    self.win_from = FROM_DISCARD
                    self.win_from_player = self.get_turn()

            self.play_current_idx += 1

    def to_last_action(self):
        """Proceed to the last action.

        Raises:
            ValueError: invalid play_log string
        """

        MAX_ACTION_NUM = 300
        self.next_action(MAX_ACTION_NUM)

    def prev_action(self, step=1):
        """Rewind a action from play_log.

        Args:
            step (int): num of step to rewind

        Raises:
            ValueError: invalid play_log string
        """

        for _ in range(step):
            if self.play_current_idx == 0:
                return

            log_str = self.play_log[self.play_current_idx - 1]
            # TODO: validation
            # TODO: duplicate more than two players win
            action_str, action_player, action_tile_str = log_str[0], int(log_str[1]), log_str[2:]

            if self.play_current_idx == 1:
                prev_action_str = None
                prev_action_player = None
                prev_action_tile_str = None
            else:
                prev_log_str = self.play_log[self.play_current_idx - 2]
                # TODO: validation
                prev_action_str, prev_action_player, prev_action_tile_str = prev_log_str[0], int(prev_log_str[1]), prev_log_str[2:]

            if action_str == 'T':
                self.game_tile_manager.rewind_take(self.get_turn(), Tile(action_tile_str))
            elif action_str == 'D':
                if action_tile_str == DISCARD_TAKEN_TILE_STR:
                    self.game_tile_manager.rewind_discard_taken(self.get_turn())
                elif prev_action_str == 'T':
                    self.game_tile_manager.rewind_discard(self.get_turn(), Tile(prev_action_tile_str))
                else:
                    self.game_tile_manager.rewind_discard(self.get_turn())
            elif action_str[0] == 'C':
                chi_from = prev_action_player
                self.game_tile_manager.rewind_chi(self.get_turn(), self.get_discarded_tile(), Tile(action_tile_str))
            elif action_str == 'P':
                peng_from = prev_action_player
                self.game_tile_manager.rewind_peng(self.get_turn(), Tile(action_tile_str), peng_from)
            elif action_str == 'A':
                self.game_tile_manager.rewind_angang(self.get_turn(), Tile(action_tile_str), Tile(prev_action_tile_str))
            elif action_str == 'B':
                self.game_tile_manager.rewind_bugang(self.get_turn(), Tile(action_tile_str), Tile(prev_action_tile_str))
            elif action_str == 'Z':
                zhigang_from = prev_action_player
                self.game_tile_manager.rewind_zhigang(self.get_turn(), Tile(action_tile_str), zhigang_from)
            elif action_str[0] == 'H':
                if self.get_action() == TAKE:
                    self.win_from = FROM_WALL
                    self.win_from_player = None
                else:
                    self.win_from = FROM_DISCARD
                    self.win_from_player = self.get_turn()

            self.play_current_idx -= 1

    def to_first_action(self):
        """Rewind to the first action.

        Raises:
            ValueError: invalid play_log string
        """

        MAX_ACTION_NUM = 300
        self.prev_action(MAX_ACTION_NUM)
