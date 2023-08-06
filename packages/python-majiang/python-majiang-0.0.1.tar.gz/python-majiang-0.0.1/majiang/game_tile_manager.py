"""Manager of whole game tiles.
"""

from majiang.tile import *
from majiang.tile_field import *
from majiang.consts import *

class Singleton(object):
    """Singleton decorator.
    """

    def __init__(self, cls):
        self._cls = cls
        self._instance = {}

    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]

@Singleton
class GameTileManager(object):
    """Manage tiles in the game.

    Attributes:
        deck_tile (majiang.DeckTileField): deck tiles
        discard_tile (list of majiang.DiscardTileField): discard tiles for 4 players
        private_tile (list of majiang.PrivateTileField): private tiles for 4 players
        meld_tile (list of majiang.MeldTileField): meld tiles for 4 players
    """

    def __init__(self):
        full_deck_tile = {
            'c': [4] * 9,
            'd': [4] * 9,
            'b': [4] * 9,
            'w': [4] * 4,
            'r': [4] * 3,
            'f': [1] * 8,
        }

        self.deck_tile = DeckTileField(full_deck_tile)
        self.discard_tile = [DiscardTileField() for _ in range(4)]
        self.private_tile = [PrivateTileField() for _ in range(4)]  
        self.meld_tile = [[] for _ in range(4)]

    def init_take(self, player, tile):
        """Initialize starting tile from deck tile.

        Args:
            player (int): player
            tile (Tile): tile

        Raises:
            ValueError: more than 4 tiles for the same kind
            ValueError: less than 1 tile for the same kind
        """

        self.deck_tile.remove_tile(tile)
        self.private_tile[player].add_tile(tile)

    def take(self, player, tile):
        """Take a tile from deck tile.

        Args:
            player (int): player
            tile (Tile): tile

        Raises:
            ValueError: more than 4 tiles for the same kind
            ValueError: less than 1 tile for the same kind
        """

        self.deck_tile.remove_tile(tile)
        self.private_tile[player].take_tile(tile)

    def rewind_take(self, player, tile):
        """Rewind take action.

        Raises:
            ValueError: no taken tile in tile field
            ValueError: more than 4 tiles for the same kind
        """

        self.private_tile[player].discard_taken_tile()
        self.deck_tile.add_tile(tile)

    def discard(self, player, tile):
        """Discard a tile from private tile

        Args:
            player (int): player
            tile (Tile): tile

        Raises:
            ValueError: more than 4 tiles for the same kind
            ValueError: less than 1 tile for the same kind
        """

        self.private_tile[player].discard_tile(tile)
        self.discard_tile[player].add_tile(tile)

    def rewind_discard(self, player, prev_tile=None):
        """Rewind discard action.

        Args:
            player (int): player
            tile (Tile): tile
            prev_tile (Tile): previous discarded tile

        Raises:
            ValueError: more than 4 tiles for the same kind
            ValueError: less than 1 tile for the same kind
        """
        tile = self.discard_tile[player].ordered_tiles[-1]
        self.discard_tile[player].remove_tile()
        if prev_tile is not None:
            self.private_tile[player].add_tile(tile)
            self.private_tile[player].remove_tile(prev_tile)
            self.private_tile[player].taken_tile = prev_tile
        else:
            self.private_tile[player].add_tile(tile)

    def discard_taken(self, player):
        """Discard taken tile from private tile.

        Args:
            player (int): player

        Raises:
            ValueError: no taken tile in tile field
            ValueError: more than 4 tiles for the same kind
        """

        tile = self.private_tile[player].taken_tile
        self.private_tile[player].discard_taken_tile()
        self.discard_tile[player].add_tile(tile)

    def rewind_discard_taken(self, player):
        """Rewind discard_taken action.

        Args:
            player (int): player

        Raises:
            ValueError: no taken tile in tile field
            ValueError: more than 4 tiles for the same kind
        """

        tile = self.discard_tile[player].last_tile()
        self.discard_tile[player].remove_tile()
        self.private_tile[player].take_tile(tile)

    def chi(self, player, tile, chi_middle_tile):
        """Chi(chow) tile.

        Args:
            player (int): player
            tile (Tile): tile to chi
            chi_middle_tile (Tile): middle tile for chi block

        Raises:
            ValueError: less than 1 tile for chi
        """

        chi_from = (player + len(SEATS) - 1) % len(SEATS)
        chi_used_tile = []
        if str(tile) > str(chi_middle_tile):
            chi_used_tile.append(Tile(tile.suit + str(tile.num - 2)))
            chi_used_tile.append(Tile(tile.suit + str(tile.num - 1)))
        elif str(tile) == str(chi_middle_tile):
            chi_used_tile.append(Tile(tile.suit + str(tile.num - 1)))
            chi_used_tile.append(Tile(tile.suit + str(tile.num + 1)))
        else:
            chi_used_tile.append(Tile(tile.suit + str(tile.num + 1)))
            chi_used_tile.append(Tile(tile.suit + str(tile.num + 2)))
        for t in chi_used_tile:
            if self.private_tile[player].tiles[t.suit][t.num - 1] == 0:
                raise ValueError('There is no tile {} in {} for CHI action'.format(tile, type(self)))

        for t in chi_used_tile:
            self.private_tile[player].remove_tile(t)
        self.discard_tile[chi_from].remove_tile()
        meld_tile_field = MeldTileField(None, 0)
        meld_tile_field.add_tile(tile)
        for t in chi_used_tile:
            meld_tile_field.add_tile(t)
        self.meld_tile[player].append(meld_tile_field)

    def rewind_chi(self, player, tile, chi_middle_tile):
        """Rewind chi action.

        Args:
            player (int): player
            tile (Tile): tile to chi
            chi_middle_tile (Tile): middle tile for chi block

        Raises:
            ValueError: invalid melds to rewind
        """

        chi_from = (player + len(SEATS) - 1) % len(SEATS)
        self.meld_tile[player].pop()
        self.discard_tile[chi_from].add_tile(tile)
        chi_used_tile = []
        if str(tile) > str(chi_middle_tile):
            chi_used_tile.append(Tile(tile.suit + str(tile.num - 2)))
            chi_used_tile.append(Tile(tile.suit + str(tile.num - 1)))
        elif str(tile) == str(chi_middle_tile):
            chi_used_tile.append(Tile(tile.suit + str(tile.num - 1)))
            chi_used_tile.append(Tile(tile.suit + str(tile.num + 1)))
        else:
            chi_used_tile.append(Tile(tile.suit + str(tile.num + 1)))
            chi_used_tile.append(Tile(tile.suit + str(tile.num + 2)))
        for t in chi_used_tile:
            self.private_tile[player].add_tile(t)

    def peng(self, player, tile, peng_from):
        """Peng(pung) tile.

        Args:
            player (int): player
            tile (Tile): tile to peng
            peng_from (int): player who discarded the tile to peng

        Raises:
            ValueError: less than 2 tiles for peng
        """

        peng_idx = (player - peng_from - 1 + len(SEATS)) % len(SEATS)
        if self.private_tile[player].tiles[tile.suit][tile.num - 1] < 2:
            raise ValueError('There are less than 2 {} in {} for PENG action'.format(tile, type(self)))

        self.private_tile[player].remove_tile(tile)
        self.private_tile[player].remove_tile(tile)
        self.discard_tile[peng_from].remove_tile()
        meld_tile_field = MeldTileField(None, peng_idx)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        self.meld_tile[player].append(meld_tile_field)

    def rewind_peng(self, player, tile, peng_from):
        """Rewind peng action.

        Args:
            player (int): player
            tile (Tile): tile to peng
            peng_from (int): player who discarded the tile to peng

        Raises:
            ValueError: invalid melds to rewind
        """

        self.meld_tile[player].pop()
        self.discard_tile[peng_from].add_tile(tile)
        self.private_tile[player].add_tile(tile)
        self.private_tile[player].add_tile(tile)

    def angang(self, player, tile):
        """Angang(create a concealed kong) tile.

        Args:
            player (int): player
            tile (Tile): tile to angang

        Raises:
            ValueError: invalid melds to rewind
        """

        if str(self.private_tile[player].taken_tile) == str(tile):
            self.private_tile[player].discard_taken_tile()
        else:
            self.private_tile[player].discard_tile(tile)

        tile_str = str(tile)
        if self.private_tile[player].tiles[tile.suit][tile.num - 1] < 3:
            raise ValueError('There are less than 3 {} in {} for ANGANG action'.format(tile, type(self)))

        self.private_tile[player].remove_tile(tile)
        self.private_tile[player].remove_tile(tile)
        self.private_tile[player].remove_tile(tile)
        meld_tile_field = MeldTileField(None, None)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        self.meld_tile[player].append(meld_tile_field)

    def rewind_angang(self, player, tile, prev_tile):
        """Rewind angang action.

        Args:
            player (int): player
            tile (Tile): tile to angang

        Raises:
            ValueError: invalid melds to rewind
        """

        if str(tile) == str(prev_tile):
            self.private_tile[player].take_tile(tile)
        else:
            self.private_tile[player].add_tile(tile)
            self.private_tile[player].remove_tile(prev_tile)
            self.private_tile[player].take_tile(prev_tile)

        self.meld_tile[player].pop()
        self.private_tile[player].add_tile(tile)
        self.private_tile[player].add_tile(tile)
        self.private_tile[player].add_tile(tile)

    def bugang(self, player, tile):
        """Bugang(add a 4th tile to a melded pung to create a kong) tile.

        Args:
            player (int): player
            tile (Tile): tile to bugang

        Raises:
            ValueError: less than 1 tile for bugang
        """

        if str(self.private_tile[player].taken_tile) == str(tile):
            self.private_tile[player].discard_taken_tile()
        else:
            self.private_tile[player].discard_tile(tile)

        tile_str = str(tile)
        melded_order = None
        for idx, meld in enumerate(self.meld_tile[player]):
            meld_tile_str_list = meld.to_tile_str_list()
            if meld_tile_str_list == [tile_str, tile_str, tile_str]:
                meld_tile_field = MeldTileField(None, meld.meld_idx)
                meld_tile_field.add_tile(tile)
                meld_tile_field.add_tile(tile)
                meld_tile_field.add_tile(tile)
                meld_tile_field.add_tile(tile)
                meld = meld_tile_field
                melded_order = idx
        self.meld_tile[player][melded_order] = meld_tile_field

    def rewind_bugang(self, player, tile, prev_tile):
        """Bugang(add a 4th tile to a melded pung to create a kong) tile.

        Args:
            player (int): player
            tile (Tile): tile to bugang

        Raises:
            ValueError: invalid melds to rewind
        """

        if str(tile) == str(prev_tile):
            self.private_tile[player].take_tile(tile)
        else:
            self.private_tile[player].add_tile(tile)
            self.private_tile[player].remove_tile(prev_tile)
            self.private_tile[player].take_tile(prev_tile)

        tile_str = str(tile)
        melded_order = None
        for idx, meld in enumerate(self.meld_tile[player]):
            meld_tile_str_list = meld.to_tile_str_list()
            if meld_tile_str_list == [tile_str, tile_str, tile_str, tile_str]:
                meld_tile_field = MeldTileField(None, meld.meld_idx)
                meld_tile_field.add_tile(tile)
                meld_tile_field.add_tile(tile)
                meld_tile_field.add_tile(tile)
                meld = meld_tile_field
                melded_order = idx
        self.meld_tile[player][melded_order] = meld_tile_field

    def zhigang(self, player, tile, zhigang_idx, zhigang_from):
        """Zhigang(open a concealed pung and add a 4th tile discarded by other player to create a kong) tile.

        Args:
            player (int): player
            tile (Tile): tile to zhigang

        Raises:
            ValueError: less than 3 tiles for zhigang
        """

        if self.private_tile[player].tiles[tile.suit][tile.num - 1] < 3:
            raise ValueError('There are less than 3 {} in {} for ZHIGANG action'.format(tile, type(self)))

        self.private_tile[player].remove_tile(tile)
        self.private_tile[player].remove_tile(tile)
        self.private_tile[player].remove_tile(tile)
        self.discard_tile[zhigang_from].remove_tile()
        meld_tile_field = MeldTileField(None, zhigang_idx)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        meld_tile_field.add_tile(tile)
        self.meld_tile[player].append(meld_tile_field)

    def rewind_zhigang(self, player, tile, zhigang_from):
        """Rewind zhigang action.

        Args:
            player (int): player
            tile (Tile): tile to zhigang

        Raises:
            ValueError: invalid melds to rewind
        """

        self.meld_tile[player].pop()
        self.discard_tile[zhigang_from].add_tile(tile)
        self.private_tile[player].add_tile(tile)
        self.private_tile[player].add_tile(tile)
        self.private_tile[player].add_tile(tile)
