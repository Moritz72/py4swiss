from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.bracket import Bracket
from py4swiss.engines.dubov.criteria.abstract import QualityCriterion
from py4swiss.engines.dubov.player import Player, PlayerRole


class C9(QualityCriterion):
    """
    Implementation of the quality criterion C.9.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.5 [C9]"
    Unless it is the last round, minimise the number of times a maximum upfloater is upfloated.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all occurrences of all upfloats of maximum upfloaters."""
        if bracket.is_last_round:
            return 0
        return bracket.upfloat_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight based on the number of times a maximum upfloater was upfloated.

        Note, however, that if any of the following conditions is not fullfilled, a weight of 0 is returned instead.

        Conditon 1: One of the given players is a resident and the other one is not
        Conditon 2: The non-resident is a maximum upfloater
        Conditon 3: The current round is not the last one
        """
        weight = DynamicUint(zero)

        if bracket.is_last_round:
            return weight

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        if player_2.role == PlayerRole.RESIDENT or not player_2.is_maximum_upfloater:
            return weight

        # See C.6 for comparison
        weight |= 1
        weight <<= bracket.upfloat_bit_dict[player_2.upfloats]

        return weight
