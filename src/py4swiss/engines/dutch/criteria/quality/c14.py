from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C14(QualityCriterion):
    """
    Implementation of the quality criterion C.14.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.14"
    minimize the number of players who receive the same downfloat as two rounds before.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        if not bracket.one_round_played:
            return 0
        # See C.12.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight of either 0 or 2 - n.

        Note that n is the number of the given players who received a downfloat two rounds before but will not receive
        one this round, assuming the players are paired with each other. However, if one of the given players is neither
        an MDP nor a resident, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER or not bracket.one_round_played:
            return weight

        # See C.12 for comparison.
        player_2_equal_or_more_points = player_1.points_with_acceleration <= player_2.points_with_acceleration
        prevented_double_float_1 = (player_1.float_2 == Float.DOWN) and player_2_equal_or_more_points
        prevented_double_float_2 = player_2.float_2 == Float.DOWN
        weight |= int(prevented_double_float_1) + int(prevented_double_float_2)

        return weight
