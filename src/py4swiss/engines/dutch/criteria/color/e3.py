from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E3(ColorCriterion):
    """
    Implementation of the color criterion E.3.

    "Taking into account C.04.2.D.5, alternate the colours to the most recent time in which one
    player had white and the other black."
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        """
        Alternates the colors relative to the most recent time when one player had the white pieces
        and the other the black pieces. For this purpose any unplayed rounds are ignored for both
        players. If this never occurs the criterion is not conclusive.
        """
        colors_1 = [color for color in player_1.colors if color is not None]
        colors_2 = [color for color in player_2.colors if color is not None]

        for color_1, color_2 in zip(colors_1[::-1], colors_2[::-1]):
            if color_1 != color_2:
                return not color_1

        return None
