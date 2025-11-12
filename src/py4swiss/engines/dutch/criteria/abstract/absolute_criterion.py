from abc import ABC, abstractmethod

from py4swiss.engines.dutch.player import Player


class AbsoluteCriterion(ABC):
    """Abstract class for absolute criteria (C.1, C.2, and C.3)."""

    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """Check whether pairing the given players suffices the absolute criterion."""
        pass  # pragma: no cover
