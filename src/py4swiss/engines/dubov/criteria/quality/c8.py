from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.player import Player, PlayerRole
from py4swiss.engines.dubov.state import State
from py4swiss.engines.matching import QualityCriterion


class C8(QualityCriterion[Player, State]):
    """
    Implementation of the quality criterion C.8.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.4 [C8]"
    Unless it is the last round, minimise the number of upfloaters who are maximum upfloaters (see Article 1.8)..
    """

    @classmethod
    def get_shift(cls, state: State) -> int:
        """Return the number of bits needed to represent all residents in the bracket."""
        if state.is_last_round:
            return 0
        # See C.5.
        return state.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, state: State) -> DynamicUint:
        """
        Return a weight of 1 if all the following conditions hold (otherwise return a weight of 0).

        Conditon 1: One of the given players is a resident and the other one is not
        Conditon 2: The non-resident is not a maximum upfloater
        Conditon 3: The current round is not the last one
        """
        weight = DynamicUint(zero)

        if state.is_last_round:
            return weight

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        # See C.5 for comparison.
        weight |= int(player_2.role != PlayerRole.RESIDENT and not player_2.is_maximum_upfloater)

        return weight
