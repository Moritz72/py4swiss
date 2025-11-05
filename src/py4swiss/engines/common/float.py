from enum import Enum


class Float(int, Enum):
    """Float of a player."""

    UP = 1
    NONE = 0
    DOWN = -1
