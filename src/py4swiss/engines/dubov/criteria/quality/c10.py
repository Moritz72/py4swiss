from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.bracket import Bracket
from py4swiss.engines.dubov.criteria.abstract import QualityCriterion
from py4swiss.engines.dubov.player import Player, PlayerRole


class C10(QualityCriterion):
    """
    Implementation of the quality criterion C.10.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.6 [C.10]"
    Unless it is the last round, minimise the number of upfloaters who upfloated in the previous round.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        if bracket.is_first_round or bracket.is_last_round:
            return 0
        # See C.5.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight based on the number of times a maximum upfloater was upfloated.

        Note, however, that if any of the following conditions is not fullfilled, a weight of 0 is returned instead.

        Condition 1: One of the given players is a resident and the other one is not
        Condition 2: The non-resident was not upfloated in the previous round
        Condition 3: The current round is not the last one
        """
        weight = DynamicUint(zero)

        if bracket.is_first_round or bracket.is_last_round:
            return weight

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        if player_2.role == PlayerRole.RESIDENT:
            return weight

        # See C.5 for comparison.
        weight |= int(not player_2.previous_upfloat)

        return weight
