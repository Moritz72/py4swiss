from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.dubov.criteria.abstract import ColorCriterion
from py4swiss.engines.dubov.player import Player


class E1(ColorCriterion):
    """
    Implementation of the color criterion E.1.

    FIDE handbook: "5. Colour Allocation rules | 5.2 | 5.2.1"
    When both players have yet to play a game, if the higher ranked player (i.e. the player who has more points or, when
    points are equal, has a smaller TPN) has an odd TPN, give them the initial-colour; otherwise, give them the opposite
    colour.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> ColorPreferenceSide:
        """
        Assign colors based on the pairing number of the higher ranked player.

        If the higher ranked player has an odd pairing number given the white pieces to the higher ranked player.
        Otherwise, give the black pieces to the higher ranked player. Note that the handling of the initial color needs
        to be handled separately.
        """
        if bool(player_1.opponents) or bool(player_2.opponents):
            return ColorPreferenceSide.NONE

        if player_1 > player_2:
            if bool(player_1.number % 2):
                return ColorPreferenceSide.WHITE
            return ColorPreferenceSide.BLACK

        # This method is only ever used with player_1 being the higher ranked player. Thus, the following is not
        # necessary for test coverage.
        if bool(player_2.number % 2):  # pragma: no cover
            return ColorPreferenceSide.BLACK
        return ColorPreferenceSide.WHITE  # pragma: no cover
