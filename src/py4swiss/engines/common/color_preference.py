from enum import Enum

from pydantic import BaseModel


class ColorPreferenceSide(int, Enum):
    WHITE = 1
    NONE = 0
    BLACK = -1


class ColorPreferenceStrength(int, Enum):
    ABSOLUTE = 3
    STRONG = 2
    MILD = 1
    NONE = 0


class ColorPreference(BaseModel):
    side: ColorPreferenceSide
    strength: ColorPreferenceStrength
