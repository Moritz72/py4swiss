from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.matching.player_protocol import PlayerProtocol
from py4swiss.engines.matching.state_protocol import StateProtocol

P = TypeVar("P", bound=PlayerProtocol)
S = TypeVar("S", bound=StateProtocol)


class ColorCriterion(ABC, Generic[P, S]):
    """Abstract class for color criteria."""

    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: P, player_2: P, state: S) -> ColorPreferenceSide:
        """
        Determine which of the given players should receive the white pieces.

        Note, however, that the criterion might not be conclusive for the given players.

        The returned value should be interpreted in the following way:
            - ColorPreferenceSide.WHITE: the former player should get the white pieces
            - ColorPreferenceSide.BLACK: the latter player should get the white pieces
            - ColorPreferenceSide.NONE: the criterion is not conclusive for the given players
        """
        pass  # pragma: no cover
