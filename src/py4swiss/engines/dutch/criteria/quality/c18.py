from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C18(QualityCriterion):
    """
    Implementation of the quality criterion C.18.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.18"
    minimize the score differences of players who receive the same downfloat as two rounds
    before.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """
        Return the number of bits needed to represent all occurrences of all score differences between MDPs and
        residents in the given bracket.
        """
        if not bracket.two_rounds_played:
            return 0
        # See C.6.
        return bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight based on the score difference of the given players as well as the difference of their scores to
        the minimum score in the given bracket and their downfloats two rounds before. However, if one of the given
        players is neither an MDP nor a resident, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER or not bracket.two_rounds_played:
            return weight

        # See C.16 for comparison.
        prev_1 = player_1.float_2 == Float.DOWN
        prev_2 = player_2.float_2 == Float.DOWN
        player_1_more_points = player_1.points_with_acceleration > player_2.points_with_acceleration

        difference_1 = player_1.points_with_acceleration - bracket.min_bracket_score + 10
        difference_2 = player_2.points_with_acceleration - bracket.min_bracket_score + 10
        difference_3 = player_1.points_with_acceleration - player_2.points_with_acceleration

        weight += (zero | int(prev_1)) << bracket.score_difference_bit_dict[difference_1]
        weight += (zero | int(prev_2)) << bracket.score_difference_bit_dict[difference_2]

        if prev_1 and player_1_more_points:
            weight -= (zero | 1) << bracket.score_difference_bit_dict.get(difference_3, 0)

        return weight
