from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C7(QualityCriterion):
    """
    Implementation of the quality criterion C.7.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.7"
    if the current bracket is neither the PPB nor the CLB (see A.9): choose the set of downfloaters in order first to
    maximize the number of pairs and then to minimize the PSD (see C.5 and C.6) in the following bracket (just in the
    following bracket).
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """
        Return the number of bits needed to represent all lower residents and score differences.

        This refers to all occurrences of all score differences between MDPs and residents in the given bracket.
        """
        # Explicitly excluded by the criterion.
        if bracket.penultimate_pairing_bracket or bracket.last_pairing_bracket:
            return 0
        # See C.5 and C.6.
        return bracket.low_bracket_bits + bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight based on the score difference of the given players.

        Additionally, the difference of their scores to the minimum score in the given bracket is also taken into
        account as well as whether the given players are lower residents or not.
        """
        weight = DynamicUint(zero)

        # Explicitly excluded by the criterion.
        if bracket.penultimate_pairing_bracket or bracket.last_pairing_bracket:
            return weight

        # Only pairings with lower residents count as pairs. Thus, with this choice of weight, the maximum round pairing
        # weight sum, will maximize the pairs.
        weight |= int(player_2.role == PlayerRole.LOWER)

        weight <<= bracket.score_difference_total_bits

        # As the scores of all lower residents is the same, if the given bracket is not the PPB, and the scores of
        # potential pairs with MDPs and residents is already determined by C.6, it is sufficient to only handle double
        # floats of MDPs and residents, see C.6 for comparison.
        if player_1.role != PlayerRole.LOWER:
            difference = player_1.points_with_acceleration - bracket.min_bracket_score + 10
            weight += (zero | 1) << bracket.score_difference_bit_dict[difference]

        if player_2.role != PlayerRole.LOWER:
            difference = player_2.points_with_acceleration - bracket.min_bracket_score + 10
            weight += (zero | 1) << bracket.score_difference_bit_dict[difference]

        return weight
