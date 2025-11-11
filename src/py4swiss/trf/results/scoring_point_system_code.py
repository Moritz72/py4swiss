from enum import Enum


class ScoringPointSystemCode(str, Enum):
    """Codes to configure a scoring system as defined by javafo."""

    WIN_WITH_WHITE = "WW"
    WIN_WITH_BLACK = "BW"
    DRAW_WITH_WHITE = "WD"
    DRAW_WITH_BLACK = "BD"
    LOSS_WITH_WHITE = "WL"
    LOSS_WITH_BLACK = "BL"
    ZERO_POINT_BYE = "ZPB"
    HALF_POINT_BYE = "HPB"
    FULL_POINT_BYE = "FPB"
    PAIRING_ALLOCATED_BYE = "PAB"
    FORFEIT_WIN = "FW"
    FORFEIT_LOSS = "FL"
    WIN = "W"
    DRAW = "D"
    LOSS = "L"
