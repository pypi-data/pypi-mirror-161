python-majiang
==============

Introduction
------------
This library provides both CUI and GUI for handling MCR(Mahjong Competition Rules) game.
And we also specify a universal format for mahjong games named PMN (Portable Majiang Notation).
PyQt6 is required for GUI.

.. code:: Python

  # for CUI
  >>> from majiang import *
  >>> pmn_file = 'tests/pmn_files/example_2.pmn'
  >>> board = Board(pmn_file)
  >>> board.to_last_action()
  >>> board.get_private_tile_list(SOUTH)
  ['c7', 'c8', 'c9', 'd1', 'd2', 'd5', 'd5', 'd8', 'd8', 'd8', 'b4', 'b5', 'b6']
  >>> board.get_private_tile_list(NORTH)
  ['c4', 'c5', 'c6', 'd1', 'd2', 'b8', 'b8']
  >>> board.get_meld_tile_list(NORTH)
  [['b8', 'b7', 'b9'], ['d8', 'd7', 'd9']]
  >>> board.get_discard_tile_list(SOUTH)
  ['r2', 'r1', 'r3', 'w1', 'w2', 'w1', 'd7', 'b5', 'w1', 'c6']
  >>> board.get_fan() # There can be multiple players in duplicate MCR rule.
  [[], [(39, 1), (62, 1), (76, 1), (77, 1)], [], [(39, 1), (63, 1), (70, 1), (77, 1)]]
  >>> board.get_fan_zh()
  [[], [('花龙', 1), ('门前清', 1), ('无字', 1), ('边张', 1)], [], [('花龙', 1), ('平和', 1), ('喜相逢', 1), ('边张', 1)]]

  # for GUI
  >>> from PyQt6.QtWidgets import QApplication
  >>> from majiang import *
  >>> from majiang.graphics import *
  >>> pmn_file = 'tests/pmn_files/example_2.pmn'
  >>> app = QApplication([])
  >>> board = Board(pmn_file)
  >>> game = GameWindow(board)
  >>> sys.exit(app.exec())

Installing
----------

::

  pip install python-majiang

PMN (Portable Majiang Notation)
-------------------------------

We specify a universal format for mahjong games inspired by `PBN (Portable Majiang Notation)<https://www.tistis.nl/pbn/>`
and name it PMN (Portable Majiang Notation).

Example
^^^^^^^

::
    
  [Event "Duplicate MCR"]
  [Site "https://mahjongsoft.com/mcrm_replay.php?session=74621&game=1&table=3"]
  [Date "2022.06.25"]
  [Board "1"]
  [PWind "E"]
  [East "SIM"]
  [South "Angel Fok"]
  [West "sylvie"]
  [North "Mimi lam"]
  [Deal "c7d345677b3689w2r1f c79d12558b45w13r23f c11267db4589w334r2f c5668d279b3789w4r3f"]
  [Scoring "Duplicate"]
  [Starting "0 0 0 0"]
  [Result "-32 36 -8 36"]
  [Penalty "0 0 0 0"]
  [Play "T0r2D0r1T1b6D1w3P2w3D2w4T3b8D3r3T0d6D0r2T1r1D1r2T2r3D2b9T3d1D3w4T0c3D0w2T1c8D1r1T2b1D2z1T3w2D3z1T0w4D0z1T1d8D1r3T2b3D2b8C3b8D3b3T0w1D0z1T1w1D1z1T2b1D2z1T3b2D3z1T0b7D0b3T1w2D1z1T2r1D2c2T3c5D3z1T0c5D0c3T1d8D1w1T2d1D2c1T3c4D3c8T0c1D0z1T1d7D1z1T2d8D2c1T3d6D3c6C0c6D0b9T1b5D1z1T2c9D2z1T3b6D3z1T0c9D0z1T1w1D1z1T2d4D2d1T3w3D3z1T0c9D0z1T1c6D1z1T2c8D2d8C3d8D3d6C0d5D0d3M1M3"]
  [Fan "None 39/1.62/1.76/1.77/1 None 39/1.63/1.70/1.77/1"]

Game Layout
^^^^^^^^^^^
Refer to `PBN (Portable Majiang Notation)<https://www.tistis.nl/pbn/>` 3.2 Tokens and 3.3 Tag Pairs.

Supplemental Tags
^^^^^^^^^^^^^^^^^

Event
"""""
This value indicates the event.
It should be reasonably descriptive.

Site
""""
This value indicates the location of the event or URL for online games.
It should be reasonably descriptive.

Date
""""
This value indicates the starting date for the game.
The value should use the format "YYYY.MM.DD".

Board
"""""
This value indicates the board number of the deal.
The value should be a positive integer.
For standard (not duplicate) MCR game, the number must between 1 and 16.

East, South, West, North
""""""""""""""""""""""""
This value indicates the name of the player at the direction.

Deal
""""
This value indicates the starting tiles of each hand.
It is defined as "<East hand> <South hand> <West hand> <North hand>"
Each hand is defined as "c<nums>d<nums>b<nums>w<nums>r<nums>f<nums>" where nums are consecutive digits between 1 and 9.
The suit is represented by 'c'(Character), 'd'(Dot), 'b'(Bamboo), 'w'(Wind), 'r'(dRagon) and 'f'(Flower). The number is
given by the following <nums>.
If the suit is 'c', 'd' or 'b', then all digits in following <nums> must be an integer between 1 and 9.
If the suit is 'w', then all digits in following <nums> must be an integer between 1 and 4.
If the suit is 'r', then all digits in following <nums> must be an integer between 1 and 3.
If the suit is 'f', then all digits in following <nums> must be an integer between 1 and 8.

Scoring
""""
This value indicates the used scoring method.
The following can be used:
  MCR
  Duplicate MCR

Starting
""""""""
This value indicates the starting score.
It is defined as "<East score> <South score> <West score> <North score>".
For duplicate MCR game, all score must be 0.

Result
""""""
This value indicates the result score of the game.
It is defined as "<East score> <South score> <West score> <North score>".
For standard (not duplicate) MCR game, the sum of all must be 0.

Penalty
"""""""
This value indicates the penalty score of the game.
It is defined as "<East score> <South score> <West score> <North score>".

Play
""""
This value indicates the played tiles.
It is defined as "<play string>". A play string is defined as "<action><player><tile suit><tile num>".
The following can be used as action:
  T take
  D discard
  C chi(chow)
  P peng(pung)
  A angang(concealed kong)
  B bugang(add a 4th tile to a melded pung to create a kong)
  Z zhigang(open a concealed pung and add a 4th tile discarded by other player to create a kong)
  R replace a flower
  H hu(mahjong)
The following can be used as action:
  0 East
  1 South
  2 West
  3 North
The following can be used as tile suit:
  c Character
  d Dot
  b Bamboo
  w Wind
  r dRagon
  f Flower
An integer can be used as tile num.
If the suit is 'c', 'd' or 'b', then the num must be an integer between 1 and 9.
If the suit is 'w', then the num must be an integer between 1 and 4.
If the suit is 'r', then the num must be an integer between 1 and 3.
If the suit is 'f', then the num must be an integer between 1 and 8.

Fan
"""
This value indicates fans of the winning hand.
It is defined as "<East fan> <South fan> <West fan> <North fan>".
Each fan is defined as "<fan1 no.>/<fan1 num>.<fan2 no.>/<fan2 num>..." for winning players or "None" for not winning players.
Only one player can win in standard MCR rule.
Fan no. is an integer between 1 and 81.
Fan number indicates the number of windding fan and is an integer between 1 and 8.

Fan list
^^^^^^^^
+---------+---------------+-----------------------------------+
| Fan no. | Fan name (zh) | Fan name (en)                     |
+=========+===============+===================================+
| 1       | 大四喜        | Big Four Winds                    |
+---------+---------------+-----------------------------------+
| 2       | 大三元        | Big Three Dragons                 |
+---------+---------------+-----------------------------------+
| 3       | 绿一色        | All Green                         |
+---------+---------------+-----------------------------------+
| 4       | 九莲宝灯      | Nine Gates                        |
+---------+---------------+-----------------------------------+
| 5       | 四杠          | Four Kongs                        |
+---------+---------------+-----------------------------------+
| 6       | 连七对        | Seven Shifted Pairs               |
+---------+---------------+-----------------------------------+
| 7       | 十三幺        | Thirteen Orphans                  |
+---------+---------------+-----------------------------------+
| 8       | 清幺九        | All Terminals                     |
+---------+---------------+-----------------------------------+
| 9       | 小四喜        | Little Four Winds                 |
+---------+---------------+-----------------------------------+
| 10      | 小三元        | Little Three Dragons              |
+---------+---------------+-----------------------------------+
| 11      | 字一色        | All Honours                       |
+---------+---------------+-----------------------------------+
| 12      | 四暗刻        | Four Concealed Pungs              |
+---------+---------------+-----------------------------------+
| 13      | 一色双龙会    | Pure Terminal Chows               |
+---------+---------------+-----------------------------------+
| 14      | 一色四同顺    | Quadruple Chow                    |
+---------+---------------+-----------------------------------+
| 15      | 一色四节高    | Four Pure Shifted Pungs           |
+---------+---------------+-----------------------------------+
| 16      | 一色四步高    | Four Pure Shifted Chows           |
+---------+---------------+-----------------------------------+
| 17      | 三杠          | Three Kongs                       |
+---------+---------------+-----------------------------------+
| 18      | 混幺九        | All Terminals and Honours         |
+---------+---------------+-----------------------------------+
| 19      | 七对          | Seven Pairs                       |
+---------+---------------+-----------------------------------+
| 20      | 七星不靠      | Greater Honours and Knitted Tiles |
+---------+---------------+-----------------------------------+
| 21      | 全双刻        | All Even Pungs                    |
+---------+---------------+-----------------------------------+
| 22      | 清一色        | Full Flush                        |
+---------+---------------+-----------------------------------+
| 23      | 一色三同顺    | Pure Triple Chow                  |
+---------+---------------+-----------------------------------+
| 24      | 一色三节高    | Pure Shifted Pungs                |
+---------+---------------+-----------------------------------+
| 25      | 全大          | Upper Tiles                       |
+---------+---------------+-----------------------------------+
| 26      | 全中          | Middle Tiles                      |
+---------+---------------+-----------------------------------+
| 27      | 全小          | Lower Tiles                       |
+---------+---------------+-----------------------------------+
| 28      | 清龙          | Pure Straight                     |
+---------+---------------+-----------------------------------+
| 29      | 三色双龙会    | Three-Suited Terminal Chows       |
+---------+---------------+-----------------------------------+
| 30      | 一色三步高    | Pure Shifted Chows                |
+---------+---------------+-----------------------------------+
| 31      | 全带五        | All Fives                         |
+---------+---------------+-----------------------------------+
| 32      | 三同刻        | Triple Pung                       |
+---------+---------------+-----------------------------------+
| 33      | 三暗刻        | Three Concealed Pungs             |
+---------+---------------+-----------------------------------+
| 34      | 全不靠        | Lesser Honours and Knitted Tiles  |
+---------+---------------+-----------------------------------+
| 35      | 组合龙        | Knitted Straight                  |
+---------+---------------+-----------------------------------+
| 36      | 大于五        | Upper Four                        |
+---------+---------------+-----------------------------------+
| 37      | 小于五        | Lower Four                        |
+---------+---------------+-----------------------------------+
| 38      | 三风刻        | Big Three Winds                   |
+---------+---------------+-----------------------------------+
| 39      | 花龙          | Mixed Straight                    |
+---------+---------------+-----------------------------------+
| 40      | 推不倒        | Reversible Tiles                  |
+---------+---------------+-----------------------------------+
| 41      | 三色三同顺    | Mixed Triple Chow                 |
+---------+---------------+-----------------------------------+
| 42      | 三色三节高    | Mixed Shifted Pungs               |
+---------+---------------+-----------------------------------+
| 43      | 无番和        | Chicken Hand                      |
+---------+---------------+-----------------------------------+
| 44      | 妙手回春      | Last Tile Draw                    |
+---------+---------------+-----------------------------------+
| 45      | 海底捞月      | Last Tile Claim                   |
+---------+---------------+-----------------------------------+
| 46      | 杠上开花      | Out with Replacement Tile         |
+---------+---------------+-----------------------------------+
| 47      | 抢杠和        | Rob Kong                          |
+---------+---------------+-----------------------------------+
| 48      | 双暗杠        | Two Dragon Pungs                  |
+---------+---------------+-----------------------------------+
| 49      | 碰碰和        | All Pungs                         |
+---------+---------------+-----------------------------------+
| 50      | 混一色        | Half Flush                        |
+---------+---------------+-----------------------------------+
| 51      | 三色三步高    | Mixed Shifted Chows               |
+---------+---------------+-----------------------------------+
| 52      | 五门齐        | All Types                         |
+---------+---------------+-----------------------------------+
| 53      | 全求人        | Melded Hand                       |
+---------+---------------+-----------------------------------+
| 54      | 双箭刻        | Two Dragon Pungs                  |
+---------+---------------+-----------------------------------+
| 55      | 全带幺        | Outside Hand                      |
+---------+---------------+-----------------------------------+
| 56      | 不求人        | Fully Concealed Hand              |
+---------+---------------+-----------------------------------+
| 57      | 双明杠        | Two Melded Kongs                  |
+---------+---------------+-----------------------------------+
| 58      | 和绝张        | Last Tile                         |
+---------+---------------+-----------------------------------+
| 59      | 箭刻          | Dragon Pung                       |
+---------+---------------+-----------------------------------+
| 60      | 圈风刻        | Prevalent Wind                    |
+---------+---------------+-----------------------------------+
| 61      | 门风刻        | Seat Wind                         |
+---------+---------------+-----------------------------------+
| 62      | 门前清        | Concealed Hand                    |
+---------+---------------+-----------------------------------+
| 63      | 平和          | All Chows                         |
+---------+---------------+-----------------------------------+
| 64      | 四归一        | Tile Hog                          |
+---------+---------------+-----------------------------------+
| 65      | 双同刻        | Mixed Double Pung                 |
+---------+---------------+-----------------------------------+
| 66      | 双暗刻        | Two Concealed Pungs               |
+---------+---------------+-----------------------------------+
| 67      | 暗杠          | Concealed Kong                    |
+---------+---------------+-----------------------------------+
| 68      | 断幺          | All Simples                       |
+---------+---------------+-----------------------------------+
| 69      | 一般高        | Pure Double Chow                  |
+---------+---------------+-----------------------------------+
| 70      | 喜相逢        | Mixed Double Chow                 |
+---------+---------------+-----------------------------------+
| 71      | 连六          | Short Straight                    |
+---------+---------------+-----------------------------------+
| 72      | 老少副        | Two Terminal Chows                |
+---------+---------------+-----------------------------------+
| 73      | 幺九刻        | Pung of Terminals or Honours      |
+---------+---------------+-----------------------------------+
| 74      | 明杠          | Melded Kong                       |
+---------+---------------+-----------------------------------+
| 75      | 缺一门        | One Voided Suit                   |
+---------+---------------+-----------------------------------+
| 76      | 无字          | No Honours                        |
+---------+---------------+-----------------------------------+
| 77      | 边张          | Edge Wait                         |
+---------+---------------+-----------------------------------+
| 78      | 坎张          | Closed Wait                       |
+---------+---------------+-----------------------------------+
| 79      | 单调将        | Single Wait                       |
+---------+---------------+-----------------------------------+
| 80      | 自摸          | Self-Draw                         |
+---------+---------------+-----------------------------------+
| 81      | 花牌          | Flower Tile                       |
+---------+---------------+-----------------------------------+
| 82      | 一明一暗杠    | Melded Kong and Concealed Kong    |
+---------+---------------+-----------------------------------+
