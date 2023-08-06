"""Tile field(private, meld, discard, deck, etc.) for multiple tiles.
"""

class AbstractTileField(object):
    """Abstract class for tile field (private, meld, discard, deck, etc.)

    Attributes:
        tiles (dict): tiles dict
    """

    def __init__(self, tiles=None):
        """

        Args:
            tiles (dict): tiles dict with 'c', 'd', 'b', 'w', 'r', 'f' as key and list as value

        Returns:
            AbstractTileField: AbstractTileField object
        """

        if tiles is None:
            self.tiles = {
                'c': [0] * 9,
                'd': [0] * 9,
                'b': [0] * 9,
                'w': [0] * 4,
                'r': [0] * 3,
                'f': [0] * 8,
            }
        else:
            self.tiles = tiles

    def to_tile_str_list(self):
        """Returns the list of tile string of all tiles.

        Returns:
            list: tile string of all tile
        """

        result = []
    
        for i in range(9):
            for j in range(self.tiles['c'][i]):
                result.append('c' + str(i + 1))
        for i in range(9):
            for j in range(self.tiles['d'][i]):
                result.append('d' + str(i + 1))
        for i in range(9):
            for j in range(self.tiles['b'][i]):
                result.append('b' + str(i + 1))
        for i in range(4):
            for j in range(self.tiles['w'][i]):
                result.append('w' + str(i + 1))
        for i in range(3):
            for j in range(self.tiles['r'][i]):
                result.append('r' + str(i + 1))
        for i in range(8):
            for j in range(self.tiles['f'][i]):
                result.append('f' + str(i + 1))
    
        return result

    def add_tile(self, tile):
        """Add the tile to tile field.

        Args:
            tile (Tile): Tile object to add

        Raises:
            ValueError: more than 4 tiles for the same kind
        """

        if self.tiles[tile.suit][tile.num - 1] == 4:
            raise ValueError('There are 4 {} in {} already'.format(tile, type(self)))

        self.tiles[tile.suit][tile.num - 1] += 1

    def remove_tile(self, tile):
        """Remove the tile from tile field.

        Args:
            tile (Tile): Tile object to move

        Raises:
            ValueError: less than 1 tile for the same kind
        """

        if self.tiles[tile.suit][tile.num - 1] == 0:
            raise ValueError('There is no {} in {}'.format(tile, type(self)))

        self.tiles[tile.suit][tile.num - 1] -= 1
        
    def tile_num(self):
        """Get total tile nums in tile field.

        Returns:
            int: total tile num in tile field
        """

        return sum(self.tiles['c'] + self.tiles['d'] + self.tiles['b'] + self.tiles['w'] + self.tiles['r'] + self.tiles['f'])

class AbstractOrderedTileField(AbstractTileField):
    """Abstract class for ordered tile field (meld, discard, etc.)

    Attributes:
        tiles (dict): tiles dict
        order_tiles (list of majiang.Tile): ordered tiles dict
    """

    def __init__(self, ordered_tiles=None):
        """

        Args:
            ordered_tiles (list of Tile): tiles dict with 'c', 'd', 'b', 'w', 'r', 'f' as key and list as value

        Returns:
            AbstractTileField: AbstractTileField object
        """

        super().__init__(self.ordered_tiles_to_tile_field_tiles(ordered_tiles))

        if ordered_tiles is None:
            self.ordered_tiles = []
        else:
            for tile in ordered_tiles:
                self.add_tile(tile)
            self.ordered_tiles = ordered_tiles

    def __str__(self):
        return ''.join([str(t) for t in (self.ordered_tiles)])

    @staticmethod
    def ordered_tiles_to_tile_field_tiles(tiles):
        """Convert order tiles list to tile field format tiles dict.

        Args:
            tiles (list of Tile): tiles list

        Returns:
            dict: tiles dict with 'c', 'd', 'b', 'w', 'r', 'f' as key and list as value
        """

        result = {
            'c': [0] * 9,
            'd': [0] * 9,
            'b': [0] * 9,
            'w': [0] * 4,
            'r': [0] * 3,
            'f': [0] * 8,
        }

        if not tiles is None:
            for tile in tiles:
                result[tile.suit][tile.num - 1] += 1

        return result

    def to_tile_str_list(self):
        """Returns the list of tile string of all tiles.

        Returns:
            list: tile string of all tile
        """

        return [str(t) for t in (self.ordered_tiles)]
        
    def last_tile(self):
        """Get last tile in tile field.

        Return:
            Tile: last tile in tile field
        """

        return self.ordered_tiles[-1]

    def add_tile(self, tile):
        """Add the tile to tile field.

        Args:
            tile (Tile): Tile object to add

        Raises:
            ValueError: more than 4 tiles for the same kind
        """

        super().add_tile(tile)

        self.ordered_tiles.append(tile)

    def remove_tile(self):
        """Remove the last tile from tile field.

        Raises:
            ValueError: less than 1 tile for the same kind
        """

        tile = self.last_tile()
        super().remove_tile(tile)

        self.ordered_tiles.pop()

class DeckTileField(AbstractTileField):
    """Deck tile field.
    """
    pass

class DiscardTileField(AbstractOrderedTileField):
    """Discard tile field.
    """

    pass

class PrivateTileField(AbstractTileField):
    """Private tile field.

    Attributes:
        tiles (dict): tiles dict
        taken_tile (majiang.Tile): tile taken in the current turn. None for other players
    """

    def __init__(self, tiles=None, taken_tile=None):
        """

        Args:
            tiles (dict): tiles dict
            taken_tile (Tile): tile taken in the current turn. None for other players
        """

        super().__init__(tiles)

        self.taken_tile = taken_tile

    def take_tile(self, tile):
        """Add the tile to taken tile.

        Args:
            tile (Tile): Tile object to take

        Raises:
            ValueError: more than 4 tiles for the same kind
        """

        if self.tiles[tile.suit][tile.num - 1] == 4:
            raise ValueError('There are 4 {} in {} already'.format(tile, type(self)))

        self.taken_tile = tile

    def discard_taken_tile(self):
        """Discard taken tile.

        Raises:
            ValueError: no taken tile in tile field
        """

        if self.taken_tile is None:
            raise ValueError('There is no taken_tile in {}'.format(type(self)))

        self.taken_tile = None

    def discard_tile(self, tile):
        """Discard the tile.

        Args:
            tile (Tile): Tile object to discard

        Raises:
            ValueError: less than 1 tile for the same kind
        """

        if self.tiles[tile.suit][tile.num - 1] != 0:
            self.remove_tile(tile)
        else:
            self.discard_taken_tile()

        if self.taken_tile is not None:
            self.add_tile(self.taken_tile)
            self.taken_tile = None

        
class MeldTileField(AbstractOrderedTileField):
    """Melded tile field.

    Attributes:
        tiles (dict): tiles dict
        order_tiles (list of majiang.Tile): ordered tiles dict
        meld_idx: meld tile index
    """

    def __init__(self, ordered_tiles, meld_idx):
        super().__init__(ordered_tiles)

        self.meld_idx = meld_idx
