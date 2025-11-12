from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E5(ColorCriterion):
    """
    Implementation of the color criterion E.5.

    FIDE handbook: "E Colour Allocation rules | E.5"
    If the higher ranked player has an odd pairing number, give him the initial-colour; otherwise give him the opposite
    colour.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Give the white pieces to the higher ranked player, if they have an odd pairing number. Otherwise, gives the
        black pieces to the higher ranked player. Note that the handling of the initial color needs to be handled
        separately.
        """

        if player_1 > player_2:
            if bool(player_1.number % 2):
                return ColorPreferenceSide.WHITE
            return ColorPreferenceSide.BLACK

        # This method is only ever used with player_1 being the higher ranked player. Thus, the following is not
        # necessary for test coverage.
        if bool(player_2.number % 2):  # pragma: no cover
            return ColorPreferenceSide.BLACK
        return ColorPreferenceSide.WHITE  # pragma: no cover
