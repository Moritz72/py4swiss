from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C9(QualityCriterion):
    """
    Implementation of the quality criterion C.9.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.9"
    minimize the number of topscorers or topscorers' opponents who get the same colour three times
    in a row.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        # See C.5.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight of 1 except for in the following cases:
            - either player is a lower resident
            - both players received the same color in the two previous rounds with the same color
              preference side
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER:
            return weight

        # Since having received the same color in the two previous rounds implies a color preference side of that color,
        # receiving the same color again can be prevented, if and only if the color preference sides do not match. Thus,
        # with this choice of weight, the maximum round pairing weight sum will minimize the number of pairs for which
        # this occurs.
        topscorer = player_1.top_scorer or player_2.top_scorer
        double = player_1.color_double and player_2.color_double
        conflict = player_1.color_preference.side == player_2.color_preference.side
        weight |= int(not (topscorer and double and conflict))

        return weight
