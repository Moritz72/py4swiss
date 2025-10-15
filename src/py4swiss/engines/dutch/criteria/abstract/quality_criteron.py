from abc import ABC, abstractmethod

from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.player import Player


class QualityCriterion(ABC):
    @classmethod
    @abstractmethod
    def get_shift(cls, bracket: Bracket) -> int:
        pass

    @classmethod
    @abstractmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        pass
