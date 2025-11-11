from __future__ import annotations

from enum import Enum


class ResultToken(str, Enum):
    """Result in a round result of a player."""

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

    def is_played(self) -> bool:
        """Check whether the given instance counts as a played game."""
        return self in _PLAYED

    def is_bye(self) -> bool:
        """Check whether the given instance counts as a bye."""
        return self in _IS_BYE

    def is_compatible_with(self, other: ResultToken) -> bool:
        """Check whether the given instances can constitute the full result of a game when put together."""
        return (self, other) in _COMPATIBLE


# The set of all result tokens that count as played.
_PLAYED = {
    ResultToken.WIN_NOT_RATED,
    ResultToken.DRAW_NOT_RATED,
    ResultToken.LOSS_NOT_RATED,
    ResultToken.WIN,
    ResultToken.DRAW,
    ResultToken.LOSS,
}
# The set of all result tokens that count as byes.
_IS_BYE = {
    ResultToken.HALF_POINT_BYE,
    ResultToken.FULL_POINT_BYE,
    ResultToken.PAIRING_ALLOCATED_BYE,
    ResultToken.ZERO_POINT_BYE,
}
# A set of tuples of all compatible result tokens.
_COMPATIBLE = {
    (ResultToken.FORFEIT_WIN, ResultToken.FORFEIT_LOSS),
    (ResultToken.FORFEIT_LOSS, ResultToken.FORFEIT_LOSS),
    (ResultToken.FORFEIT_LOSS, ResultToken.FORFEIT_WIN),
    (ResultToken.WIN_NOT_RATED, ResultToken.LOSS_NOT_RATED),
    (ResultToken.LOSS_NOT_RATED, ResultToken.WIN_NOT_RATED),
    (ResultToken.DRAW_NOT_RATED, ResultToken.DRAW_NOT_RATED),
    (ResultToken.WIN, ResultToken.LOSS),
    (ResultToken.LOSS, ResultToken.WIN),
    (ResultToken.DRAW, ResultToken.DRAW),
}
