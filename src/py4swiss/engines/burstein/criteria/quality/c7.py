from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.burstein.player import Player, PlayerRole
from py4swiss.engines.burstein.state import State
from py4swiss.engines.matching import QualityCriterion


class C7(QualityCriterion[Player, State]):
    """
    Implementation of the quality criterion C.7.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.3 [C.7]"
    Choose the outgoing floaters so that in the following bracket every criterion from [C1] to [C6] (see Articles 2.1 to
    2.3.2) is complied with.
    """

    @classmethod
    def get_shift(cls, state: State) -> int:
        """Return the number of bits needed to represent all residents in the lower bracket as well as all scores."""
        # See C.5 and C.6 for comparison.
        return state.lower_bits + state.resident_score_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, state: State) -> DynamicUint:
        """Return a weight based on the roles and scores of the given players."""
        weight = DynamicUint(zero)

        # Only pairings of a residents of the current or lower bracket are considered.
        if PlayerRole.NONE in (player_1.role, player_2.role):
            return weight

        # See C.5 for comparison.
        # This choice maxmimizes the number of pairs in the lower bracket in sum.
        weight |= int(player_1.role >= PlayerRole.LOWER and player_2.role == PlayerRole.LOWER)
        weight <<= state.resident_score_total_bits

        # See C.6 for comparison.
        # The weight contains all 0s except for a single 1 accounting for the score of the resident involved in thus
        # pair. Thus, in sum this choice of weights will maximize the score of outgoing floaters paired in the lower
        # bracket which means the scores of outgoing floaters in the lower bracket is minimized.
        if player_1.role == PlayerRole.RESIDENT:
            weight += (zero | 1) << state.resident_score_bit_dict[player_1.points_with_acceleration]

        return weight
