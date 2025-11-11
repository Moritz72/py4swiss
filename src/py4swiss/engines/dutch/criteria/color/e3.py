from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E3(ColorCriterion):
    """
    Implementation of the color criterion E.3.

    FIDE handbook: "E Colour Allocation rules | E.3"
    Taking into account C.04.2.D.5, alternate the colours to the most recent time in which one player had white and the
    other black.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Alternate the colors relative to the most recent time when one player had the white pieces and the other the
        black pieces. For this purpose any unplayed rounds are ignored for both players. If this never occurs the
        criterion is not conclusive.
        """

        for color_1, color_2 in zip(player_1.colors[::-1], player_2.colors[::-1], strict=False):
            if color_1 != color_2:
                if color_1:
                    return ColorPreferenceSide.BLACK
                return ColorPreferenceSide.WHITE

        return ColorPreferenceSide.NONE
