from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py4swiss.engines.matching.player_protocol import PlayerProtocol

P = TypeVar("P", bound=PlayerProtocol)


class AbsoluteCriterion(ABC, Generic[P]):
    """Abstract class for absolute criteria."""

    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: P, player_2: P) -> bool:
        """Check whether pairing the given players suffices the absolute criterion."""
        pass  # pragma: no cover
