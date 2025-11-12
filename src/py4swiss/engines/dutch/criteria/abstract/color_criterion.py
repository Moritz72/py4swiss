from abc import ABC, abstractmethod

from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dutch.player import Player


class ColorCriterion(ABC):
    """Abstract class for color criteria (E.1 - E.5)."""

    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Check whether the color criterion can be applied to the given players and if so, determine which of the given
        players should receive the white pieces.

        The returned value should be interpreted in the following way:
            - ColorPreferenceSide.WHITE: the former player should get the white pieces
            - ColorPreferenceSide.BLACK: the latter player should get the white pieces
            - ColorPreferenceSide.NONE: the criterion is not conclusive for the given players
        """

        pass  # pragma: no cover
