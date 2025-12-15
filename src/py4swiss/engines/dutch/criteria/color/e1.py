from py4swiss.engines.common.color_preference import ColorPreferenceSide
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E1(ColorCriterion):
    """
    Implementation of the color criterion E.1.

    FIDE handbook: "E Colour Allocation rules | E.1"
    Grant both colour preferences.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Grant both color preferences, if possible.

        This is the case if and only if the given players have opposing color preference sides. Otherwise, the criterion
        is not conclusive.
        """
        exists = player_1.color_preference.side and player_2.color_preference.side
        no_conflict = player_1.color_preference.side != player_2.color_preference.side

        if exists and no_conflict:
            return player_1.color_preference.side

        return ColorPreferenceSide.NONE
