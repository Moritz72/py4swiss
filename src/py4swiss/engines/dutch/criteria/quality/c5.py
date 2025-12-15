from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C5(QualityCriterion):
    """
    Implementation of the quality criterion C.5.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.5"
    maximize the number of pairs (equivalent to: minimize the number of downfloaters).
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        # Since the weight for each pair will be at most 1, the number of residents in the bracket will always be
        # greater than the sum of all weights.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """Return a weight of 1, if both players are either MDPs or residents, else 0."""
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs. Thus, with this choice of weight, the maximum round
        # pairing weight sum will maximize the number of pairs.
        weight |= int(player_2.role != PlayerRole.LOWER)

        return weight
