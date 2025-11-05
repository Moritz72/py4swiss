from py4swiss.engines.dutch.criteria.abstract import ColorCriterion
from py4swiss.engines.dutch.player import Player


class E5(ColorCriterion):
    """
    Implementation of the color criterion E.5.

    "If the higher ranked player has an odd pairing number, give him the initial-colour; otherwise
    give him the opposite colour."
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool | None:
        """
        Gives the white pieces to the higher ranked player, if they have an odd pairing number.
        Otherwise, gives the black pieces to the higher ranked player. Note that the handling of
        the initial color needs to be handled separately.
        """

        if player_1.number < player_2.number:
            return bool(player_1.number % 2)
        return not bool(player_2.number % 2)
