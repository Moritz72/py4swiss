from abc import ABC, abstractmethod

from py4swiss.engines.dutch.player import Player


class ColorCriterion(ABC):
    """Abstract class for color criteria (E.1 - E.5)."""

    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        """
        Check whether the color criterion can be applied to the given players and if so, determine
        which of the given players should receive the white pieces.

        The returned value should be interpreted in the following way:
            - `ColorPreferenceSide.WHITE`: `player_1` should get the white pieces
            - `ColorPreferenceSide.BLACK`: `player_1` should get the black pieces
            - `ColorPreferenceSide.NONE`: the criterion is not conclusive for the given players
        """

        pass
