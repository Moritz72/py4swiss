from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C17(QualityCriterion):
    """
    Implementation of the quality criterion C.17.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.17"
    minimize the score differences of players who receive the same upfloat as the previous round.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """
        Return the number of bits needed to represent all occurrences of all score differences between MDPs and
        residents in the given bracket.
        """
        if not bracket.one_round_played:
            return 0
        # See C.6
        return bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight based on the score difference of the given players as well as the difference of their scores to
        the minimum score in the given bracket and their upfloats in the previous round. However, if one of the given
        players is neither an MDP nor a resident, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER or not bracket.one_round_played:
            return weight

        # See C.6 for comparison. Note that, similar to C.13, only the lower ranked player can upfloat and unpaired
        # players never upfloat.
        player_1_more_points = player_1.points_with_acceleration > player_2.points_with_acceleration
        double_float = (player_2.float_1 == Float.UP) and player_1_more_points
        difference = player_1.points_with_acceleration - bracket.min_bracket_score + 10
        weight -= (zero | int(double_float)) << bracket.score_difference_bit_dict[difference]

        return weight
