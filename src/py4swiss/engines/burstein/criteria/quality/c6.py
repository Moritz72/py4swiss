from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.burstein.player import Player, PlayerRole
from py4swiss.engines.burstein.state import State
from py4swiss.engines.matching import QualityCriterion


class C6(QualityCriterion[Player, State]):
    """
    Implementation of the quality criterion C.6.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.2 [C6]"
    Minimise the scores (taken in descending order) of the outgoing floaters.
    """

    @classmethod
    def get_shift(cls, state: State) -> int:
        """
        Return the number of bits needed to represent resident scores.

        This refers to all occurrences of all scores between of residents in the given bracket.
        """
        # Since each occurrence of a score will be contained in at most one weight, the number of bits needed to
        # represent all such occurrences will always be greater than the sum of all weights in a round pairing.
        return state.resident_score_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, state: State) -> DynamicUint:
        """
        Return a weight based on the scores of the given players.

        However, if one of them is not a resident, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings of residents are considered.
        if player_1.role != PlayerRole.RESIDENT or player_2.role != PlayerRole.RESIDENT:
            return weight

        # The weight contains all 0s except for two 1s accounting for the scores of the player involved in thus pair.
        # Thus, in sum this choice of weights will maximize the score of players paired in the current bracket which
        # means the scores of outgoing floaters are minimized.
        weight += (zero | 1) << state.resident_score_bit_dict[player_1.points_with_acceleration]
        weight += (zero | 1) << state.resident_score_bit_dict[player_2.points_with_acceleration]

        return weight
