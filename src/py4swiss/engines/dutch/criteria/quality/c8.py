from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C8(QualityCriterion):
    """
    Implementation of the quality criterion C.8.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.8"
    minimize the number of topscorers or topscorers' opponents who get a colour difference higher than +2 or lower than
    -2.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        # See C.5.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight of 1 except for some special cases.

        Case 1: Either player is a lower resident
        Case 2: Both the color differences of both players are greater than 1 in absolute value with the same color
                preference side
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER:
            return weight

        # Since a color difference of +2 or -2 implies a color preference side of that color, a difference higher than
        # +2 or lower than -2 can be prevented, if and only if the color preference sides do not match. Thus, with this
        # choice of weight, the maximum round pairing weight sum will minimize the number of pairs for which this
        # occurs.
        topscorer = player_1.top_scorer or player_2.top_scorer
        at_least_2 = abs(player_1.color_difference) > 1 and abs(player_2.color_difference) > 1
        conflict = player_1.color_preference.side == player_2.color_preference.side
        weight |= int(not (topscorer and at_least_2 and conflict))

        return weight
