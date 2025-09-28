from __future__ import annotations

from enum import Enum


class ResultToken(str, Enum):
    FORFEIT_LOSS = "-"
    FORFEIT_WIN = "+"
    WIN_NOT_RATED = "W"
    DRAW_NOT_RATED = "D"
    LOSS_NOT_RATED = "L"
    WIN = "1"
    DRAW = "="
    LOSS = "0"
    HALF_POINT_BYE = "H"
    FULL_POINT_BYE = "F"
    PAIRING_ALLOCATED_BYE = "U"
    ZERO_POINT_BYE = "Z"

    _COMPATIBLE = {
        (FORFEIT_WIN, FORFEIT_LOSS),
        (FORFEIT_LOSS, FORFEIT_LOSS),
        (FORFEIT_LOSS, FORFEIT_WIN),
        (WIN_NOT_RATED, LOSS_NOT_RATED),
        (LOSS_NOT_RATED, WIN_NOT_RATED),
        (DRAW_NOT_RATED, DRAW_NOT_RATED),
        (WIN, LOSS),
        (LOSS, WIN),
        (DRAW, DRAW)
    }

    def is_compatible_with(self, other: ResultToken) -> bool:
        return (self, other) in self._COMPATIBLE
