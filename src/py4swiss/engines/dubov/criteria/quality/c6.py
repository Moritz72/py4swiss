from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.player import Player, PlayerRole
from py4swiss.engines.dubov.state import State
from py4swiss.engines.matching import QualityCriterion


class C6(QualityCriterion[Player, State]):
    """
    Implementation of the quality criterion C.6.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.2 [C6]"
    Minimise the score differences (taken in descending order) in the pairs involving upfloaters, i.e. maximise the
    scores (taken in ascending order) of the upfloaters.
    """

    @classmethod
    def get_shift(cls, state: State) -> int:
        """
        Return the number of bits needed to represent score differences.

        This refers to all occurrences of all score differences between residents and upfloaters in the given bracket.
        """
        # Since each occurrence of a score difference will be contained in at most one weight, the number of bits needed
        # to represent all such occurrences will always be greater than the sum of all weights in a round pairing.
        return state.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, state: State) -> DynamicUint:
        """
        Return a weight based on the score difference of the given players.

        However, if they are both residents or both non-residents, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        if player_2.role == PlayerRole.RESIDENT:
            return weight

        difference = player_1.points_with_acceleration - player_2.points_with_acceleration

        # The weight contains all 0s except for possbily one 1 accounting for the introduced score difference by this
        # pair. Thus, in sum this choice of weights will minimize the score difference of the full round pairing.
        weight |= 1
        weight <<= state.score_difference_bit_dict[difference]

        return weight
