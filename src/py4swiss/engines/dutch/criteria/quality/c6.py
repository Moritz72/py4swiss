from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C6(QualityCriterion):
    """
    Implementation of the quality criterion C.6.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.6"
    minimize the PSD (This basically means: maximize the number of paired MDP(s); and, as far as possible, pair the ones
    with the highest scores).
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """
        Return the number of bits needed to represent score differences.

        This refers to all occurrences of all score differences between MDPs and residents in the given bracket.
        """
        # Since each occurrence of a score difference will be contained in at most one weight, the number of bits needed
        # to represent all such occurrences will always be greater than the sum of all weights in a round pairing.
        return bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight based on the score difference of the given players.

        Additionally, the difference of their scores to the minimum score in the given bracket is also taken into
        account. However, if one of the given players is neither an MDP nor a resident, then a weight of 0 will be
        returned.
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER:
            return weight

        # FIDE handbook: "A.8 Pairing Score Difference (PSD)"
        # For each downfloater, the SD is defined as the difference between the score of the downfloater, and an
        # artificial value that is one point less than the score of the lowest ranked player of the current bracket
        # (even when this yields a negative value).
        difference_1 = player_1.points_with_acceleration - bracket.min_bracket_score + 10
        difference_2 = player_2.points_with_acceleration - bracket.min_bracket_score + 10
        difference_3 = player_1.points_with_acceleration - player_2.points_with_acceleration

        # The weight counts the number of score differences caused by downfloats that will not occur as well as a malus
        # for the score difference that does occur, if this pair is selected in separate parts of the weight based on
        # the absolute value of the given difference. Thus, with this choice of weight, the maximum round pairing weight
        # sum will minimize the PSD. Note that the weight will always be positive, since the score bracket bits are
        # increasing as a function of the score difference.
        weight += (zero | 1) << bracket.score_difference_bit_dict[difference_1]
        weight += (zero | 1) << bracket.score_difference_bit_dict[difference_2]
        weight -= (zero | 1) << bracket.score_difference_bit_dict.get(difference_3, 0)

        return weight
