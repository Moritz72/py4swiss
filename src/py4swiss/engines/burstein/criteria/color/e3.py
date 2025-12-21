from py4swiss.engines.burstein.player import Player
from py4swiss.engines.burstein.state import State
from py4swiss.engines.common.color_preference import ColorPreferenceSide
from py4swiss.engines.matching import ColorCriterion


class E3(ColorCriterion[Player, State]):
    """
    Implementation of the color criterion E.3.

    FIDE handbook: "5. Colour Allocation rules | 5.2 | 5.2.3"
    Grant the stronger colour preference.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player, state: State) -> ColorPreferenceSide:
        """
        Grant the stronger color preference.

        If there is a difference in strength between the given players grant the stonger one. Otherwise, the criterion
        is not conclusive.
        """
        is_same_strength = player_1.color_preference.strength == player_2.color_preference.strength

        if not is_same_strength:
            if player_1.color_preference.strength > player_2.color_preference.strength:
                return player_1.color_preference.side
            return player_2.color_preference.side.get_opposite()

        return ColorPreferenceSide.NONE
