"""Majiang tile.
"""

class Tile(object):
    """Majiang tile.

    A valid string format for a tile is '<number><suit>' where <number> is an integer and <suit> is one if
    'c'(Character), 'd'(Dot), 'b'(Bamboo), 'w'(Wind), 'r'(dRagon) and 'f'(Flower).

    If <suit> is 'c', 'd' or 'b', then <number> must be an integer between 1 and 9.
    If <suit> is 'w', then <number> must be an integer between 1 and 4.
    If <suit> is 'r', then <number> must be an integer between 1 and 3.
    If <suit> is 'f', then <number> must be an integer between 1 and 8.

    Attributes:
        tile_str (str): tile string
        suit (str): suit of the tile
        num (int): num of the tile
    """

    def __init__(self, tile_str):
        """

        Args:
            tile_str (str): tile string

        Returns:
            Tile: Tile object

        Raises:
            ValueError: parsing invalid tile string
        """

        self.tile_str = tile_str

        if len(tile_str) != 2:
            raise ValueError('Tile string {} is not valid'.format(tile_str))

        try:
            suit, num = tile_str[0], int(tile_str[1])
        except:
            raise ValueError('Tile string {} is not valid'.format(tile_str))

        if not self.is_valid(tile_str):
            raise ValueError('Tile string {} is not valid'.format(tile_str))

        self.suit = suit
        self.num = num

    def __str__(self):
        return self.tile_str

    @staticmethod
    def is_valid(tile_str):
        """Judge whether the tile_str is a valid tile string.

        Args:
            tile_str (str): tile string

        Returns:
            bool: where tile_str is valid
        """

        if len(tile_str) != 2:
            return False

        try:
            suit, num = tile_str[0], int(tile_str[1])
        except:
            return False

        if not suit in ['c', 'd', 'b', 'w', 'r', 'f']:
            return False

        if num < 1:
            return False

        if suit in ['c', 'd', 'b'] and num > 9:
            return False

        if suit == 'w' and num > 4:
            return False

        if suit == 'r' and num > 3:
            return False

        if suit == 'f' and num > 8:
            return False

        return True
