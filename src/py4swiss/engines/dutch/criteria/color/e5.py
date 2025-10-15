from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E5(ColorCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        if player_1.number < player_2.number:
            return bool(player_1.number % 2)
        return not bool(player_2.number % 2)
