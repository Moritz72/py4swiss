from abc import ABC, abstractmethod

from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.player import Player


class QualityCriterion(ABC):
    """Abstract class for quality criteria (C.5 - C.19)."""

    @classmethod
    @abstractmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits are needed to hold the maximum round pairing weight sum of the given bracket."""
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """Return the criterion weight for the given players and bracket."""
        pass  # pragma: no cover
