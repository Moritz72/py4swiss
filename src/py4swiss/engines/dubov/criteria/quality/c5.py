from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.bracket import Bracket
from py4swiss.engines.dubov.criteria.abstract import QualityCriterion
from py4swiss.engines.dubov.player import Player, PlayerRole


class C5(QualityCriterion):
    """
    Implementation of the quality criterion C.5.

    FIDE handbook: "2 Pairing Criteria | 2.3 Quality Criteria | 2.3.1 [C5]"
    Minimise the number of upfloaters.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        # Since the weight for each pair will be at most 1, the number of residents in the bracket will always be
        # greater than the sum of all weights.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """Return a weight of 1, if the given players are both residents, else 0."""
        weight = DynamicUint(zero)

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        # Pairings between residents require no upfloaters while any other pairings involving residents require exactly
        # one upfloater. Thus, with this choice of weight, the maximum round pairing weight sum will maximize the number
        # of pairs.
        weight |= int(player_2.role == PlayerRole.RESIDENT)

        return weight
