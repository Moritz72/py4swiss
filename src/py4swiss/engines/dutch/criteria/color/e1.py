from py4swiss.engines.common.color_preference import ColorPreferenceSide
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E1(ColorCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        exists = player_1.color_preference.side and player_2.color_preference.side
        no_conflict = player_1.color_preference.side != player_2.color_preference.side

        if exists and no_conflict:
            return player_1.color_preference.side == ColorPreferenceSide.WHITE

        return None
