from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dubov.criteria.abstract import ColorCriterion
from py4swiss.engines.dubov.player import Player


class E4(ColorCriterion):
    """
    Implementation of the color criterion E.4.

    FIDE handbook: "5. Colour Allocation rules | 5.2 | 5.2.4"
    Alternate the colours to the most recent time in which one player had White and the other Black.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Alternate the colors relative to the most recent time when the players had opposing piece colors.

        For this purpose any unplayed rounds are ignored for both players. If this never occurs the criterion is not
        conclusive.
        """
        for color_1, color_2 in zip(player_1.colors[::-1], player_2.colors[::-1], strict=False):
            if color_1 != color_2:
                if color_1:
                    return ColorPreferenceSide.BLACK
                return ColorPreferenceSide.WHITE

        return ColorPreferenceSide.NONE
