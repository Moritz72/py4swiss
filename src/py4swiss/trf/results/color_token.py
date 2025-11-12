from enum import Enum


class ColorToken(str, Enum):
    """Color in a round result of a player."""

    WHITE = "w"
    BLACK = "b"
    BYE_OR_NOT_PAIRED = "-"
