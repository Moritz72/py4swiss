from abc import ABC, abstractmethod

from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dutch.player import Player


class ColorCriterion(ABC):
    """Abstract class for color criteria (E.1 - E.5)."""

    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Determine which of the given players should receive the white pieces.

        Note, however, that the criterion might not be conclusive for the given players.

        The returned value should be interpreted in the following way:
            - ColorPreferenceSide.WHITE: the former player should get the white pieces
            - ColorPreferenceSide.BLACK: the latter player should get the white pieces
            - ColorPreferenceSide.NONE: the criterion is not conclusive for the given players
        """
        pass  # pragma: no cover
