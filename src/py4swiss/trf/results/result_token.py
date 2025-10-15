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

    def is_compatible_with(self, other: ResultToken) -> bool:
        return (self, other) in _COMPATIBLE


_COMPATIBLE = {
    (ResultToken.FORFEIT_WIN, ResultToken.FORFEIT_LOSS),
    (ResultToken.FORFEIT_LOSS, ResultToken.FORFEIT_LOSS),
    (ResultToken.FORFEIT_LOSS, ResultToken.FORFEIT_WIN),
    (ResultToken.WIN_NOT_RATED, ResultToken.LOSS_NOT_RATED),
    (ResultToken.LOSS_NOT_RATED, ResultToken.WIN_NOT_RATED),
    (ResultToken.DRAW_NOT_RATED, ResultToken.DRAW_NOT_RATED),
    (ResultToken.WIN, ResultToken.LOSS),
    (ResultToken.LOSS, ResultToken.WIN),
    (ResultToken.DRAW, ResultToken.DRAW)
}
