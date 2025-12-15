from py4swiss.engines.common.color_preference import (
    ColorPreferenceSide,
    ColorPreferenceStrength,
)
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E2(ColorCriterion):
    """
    Implementation of the color criterion E.2.

    FIDE handbook: "E Colour Allocation rules | E.2"
    Grant the stronger colour preference. If both are absolute (topscorers, see A.7) grant the wider colour difference
    (see A.6).
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Grant the stronger color preference.

        If there is a difference in strength between the given players grant the stonger one. Otherwise, if the color
        preference strength is absolute, grant the one with the bigger difference between games with the white and black
        pieces, if they are not the same. If none of the above applies, the criterion is not conclusive.
        """
        is_same_strength = player_1.color_preference.strength == player_2.color_preference.strength
        is_same_difference = abs(player_1.color_difference) == abs(player_2.color_difference)
        is_absolute = all(p.color_preference.strength == ColorPreferenceStrength.ABSOLUTE for p in (player_1, player_2))

        if not is_same_strength:
            if player_1.color_preference.strength > player_2.color_preference.strength:
                return player_1.color_preference.side
            return player_2.color_preference.side.get_opposite()

        if is_absolute and not is_same_difference:
            if abs(player_1.color_difference) > abs(player_2.color_difference):
                return player_1.color_preference.side
            return player_2.color_preference.side.get_opposite()

        return ColorPreferenceSide.NONE
