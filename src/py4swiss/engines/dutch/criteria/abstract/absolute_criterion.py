from abc import ABC, abstractmethod

from py4swiss.engines.dutch.player import Player


class AbsoluteCriterion(ABC):
    @classmethod
    @abstractmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        pass
