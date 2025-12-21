from py4swiss.engines.burstein.player import Player
from py4swiss.engines.burstein.state import State
from py4swiss.engines.common import ColorPreferenceSide
from py4swiss.engines.matching import ColorCriterion


class E1(ColorCriterion[Player, State]):
    """
    Implementation of the color criterion E.1.

    FIDE handbook: "5. Colour Allocation rules | 5.2 | 5.2.1"
    When both players have yet to play a game, if the higher ranked player (i.e. the player who has more points or, when
    points are equal, has a smaller TPN) has an odd TPN, give them the initial-colour; otherwise, give them the opposite
    colour.
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player, state: State) -> ColorPreferenceSide:
        """
        Assign colors based on the pairing number of the higher ranked player.

        If the higher ranked player has an odd pairing number given them the initial color. Otherwise, give the intial
        color to the other player. However, this criterion only applies if the given players has yet to play a game.
        """
        if bool(player_1.opponents) or bool(player_2.opponents):
            return ColorPreferenceSide.NONE

        swap_side = not state.initial_color

        # This method is only ever used with player_1 being the higher ranked player. Thus, the following is not
        # necessary for test coverage.
        if player_2 > player_1:  # pragma: no cover
            player_1, player_2 = player_2, player_1
            swap_side = not swap_side

        if bool(player_1.number % 2):
            side = ColorPreferenceSide.WHITE
        else:
            side = ColorPreferenceSide.BLACK

        if swap_side:
            side = side.get_opposite()

        return side
