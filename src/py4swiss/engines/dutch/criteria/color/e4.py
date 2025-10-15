from py4swiss.engines.common.color_preference import ColorPreferenceSide
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E4(ColorCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        if player_1 > player_2 and bool(player_1.color_preference.side):
            return player_1.color_preference.side == ColorPreferenceSide.WHITE

        if player_2 > player_1 and bool(player_2.color_preference.side):
            return player_2.color_preference.side == ColorPreferenceSide.BLACK

        return None
