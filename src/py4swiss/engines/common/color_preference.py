from enum import Enum
from typing import Self

from pydantic import BaseModel


class ColorPreferenceSide(int, Enum):
    """Color preference side of a player."""

    WHITE = 1
    NONE = 0
    BLACK = -1

    def get_opposite(self) -> Self:
        """Return the opposite side to the given one."""
        return ColorPreferenceSide(-int(self))


class ColorPreferenceStrength(int, Enum):
    """Color preference strength of a player."""

    ABSOLUTE = 3
    STRONG = 2
    MILD = 1
    NONE = 0


class ColorPreference(BaseModel):
    """Color preference of a player."""

    side: ColorPreferenceSide
    strength: ColorPreferenceStrength
