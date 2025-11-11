from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ColorPreferenceSide(int, Enum):
    """Color preference side of a player."""

    WHITE = 1
    NONE = 0
    BLACK = -1

    def get_opposite(self) -> ColorPreferenceSide:
        """Return the opposite side to the given one."""
        return ColorPreferenceSide(-int(self))

    def conflicts(self, other: ColorPreferenceSide) -> bool:
        """Check whether the given sides conflict with each other e.g. (white, white) or (black, black)."""
        return self == other and self is not ColorPreferenceSide.NONE


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
