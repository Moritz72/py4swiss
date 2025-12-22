from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.matching.player_protocol import PlayerProtocol
from py4swiss.engines.matching.state_protocol import StateProtocol

P = TypeVar("P", bound=PlayerProtocol)
S = TypeVar("S", bound=StateProtocol)


class QualityCriterion(ABC, Generic[P, S]):
    """Abstract class for quality criteria."""

    @classmethod
    @abstractmethod
    def get_shift(cls, state: S) -> int:
        """Return the number of bits are needed to hold the maximum round pairing weight sum of the given state."""
        pass  # pragma: no cover

    @classmethod
    @abstractmethod
    def get_weight(cls, player_1: P, player_2: P, zero: DynamicUint, state: S) -> DynamicUint:
        """Return the criterion weight for the given players and state."""
        pass  # pragma: no cover
