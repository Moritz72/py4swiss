from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.player import Player, PlayerRole
from py4swiss.engines.dubov.state import State
from py4swiss.engines.matching import QualityCriterion


class C10(QualityCriterion[Player, State]):
    """
    Implementation of the quality criterion C.10.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.6 [C.10]"
    Unless it is the last round, minimise the number of upfloaters who upfloated in the previous round.
    """

    @classmethod
    def get_shift(cls, state: State) -> int:
        """Return the number of bits needed to represent all residents in the bracket."""
        if state.is_first_round or state.is_last_round:
            return 0
        # See C.5.
        return state.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, state: State) -> DynamicUint:
        """
        Return a weight based on the number of times a maximum upfloater was upfloated.

        Note, however, that if any of the following conditions is not fullfilled, a weight of 0 is returned instead.

        Condition 1: One of the given players is a resident and the other one is not
        Condition 2: The non-resident was not upfloated in the previous round
        Condition 3: The current round is not the last one
        """
        weight = DynamicUint(zero)

        if state.is_first_round or state.is_last_round:
            return weight

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        if player_2.role == PlayerRole.RESIDENT:
            return weight

        # See C.5 for comparison.
        weight |= int(not player_2.previous_upfloat)

        return weight
