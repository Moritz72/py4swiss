from py4swiss.engines.common.color_preference import ColorPreferenceSide, ColorPreferenceStrength
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E2(ColorCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        is_same_strength = player_1.color_preference.strength == player_2.color_preference.strength
        is_same_difference = abs(player_1.color_difference) == abs(player_2.color_difference)
        is_absolute = all(p.color_preference.strength == ColorPreferenceStrength.ABSOLUTE for p in (player_1, player_2))

        if not is_same_strength:
            if player_1.color_preference.strength > player_2.color_preference.strength:
                return player_1.color_preference.side == ColorPreferenceSide.WHITE
            return player_2.color_preference.side == ColorPreferenceSide.BLACK

        if is_absolute and not is_same_difference:
            if abs(player_1.color_difference) > abs(player_2.color_difference):
                return player_1.color_preference.side == ColorPreferenceSide.WHITE
            return player_2.color_preference.side == ColorPreferenceSide.BLACK

        return None
