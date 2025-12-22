from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.burstein.player import Player, PlayerRole
from py4swiss.engines.burstein.state import State
from py4swiss.engines.matching import QualityCriterion


class C5(QualityCriterion[Player, State]):
    """
    Implementation of the quality criterion C.5.

    FIDE handbook: "2 Pairing Criteria | 2.3 Quality Criteria | 2.3.1 [C5]"
    Maximise the number of pairs (equivalent to: minimise the number of outgoing floaters).
    """

    @classmethod
    def get_shift(cls, state: State) -> int:
        """Return the number of bits needed to represent all residents in the bracket."""
        # Since the weight for each pair will be at most 1, the number of residents in the bracket will always be
        # greater than the sum of all weights.
        return state.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, state: State) -> DynamicUint:
        """Return a weight of 1, if the given players are both residents, else 0."""
        weight = DynamicUint(zero)

        # Only pairings between residents count as pairs.
        if player_1.role != PlayerRole.RESIDENT or player_2.role != PlayerRole.RESIDENT:
            return weight

        weight |= 1

        return weight
