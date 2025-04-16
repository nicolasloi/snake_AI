"""
Entities for Snake AI Game
"""

from enum import Enum
from collections import namedtuple

class Direction(Enum):
    """
    Possible directions for the snake
    """
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Points to represent positions in the grid
Point = namedtuple('Point', 'x, y')