from py4swiss.engines.common.color_preference import ColorPreferenceSide
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E4(ColorCriterion):
    """
    Implementation of the color criterion E.4.

    FIDE handbook: "E Colour Allocation rules | E.4"
    Grant the colour preference of the higher ranked player.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Grant the color preference of the player with the higher rank. If they do not have one, this criterion is not
        conclusive.
        """

        if player_1 > player_2 and bool(player_1.color_preference.side):
            return player_1.color_preference.side

        # This method is only ever used with player_1 being the higher ranked player. Thus, the following is not
        # necessary for test coverage.
        if player_2 > player_1 and bool(player_2.color_preference.side):  # pragma: no cover
            return player_2.color_preference.side.get_opposite()

        return ColorPreferenceSide.NONE
