from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C10(QualityCriterion):
    """
    Implementation of the quality criterion C.10.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.10"
    minimize the number of players who do not get their colour preference.
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
            - both players have the same color preference side
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER:
            return weight

        # There will be a player in a pair who does not get their color preference, if and only if both players in the
        # pair have the same color preference side. Furthermore, at least one player in each pair will get their color
        # preference. Thus, with this choice of weight, the maximum round pairing weight sum will minimize the number of
        # paired players that do not get their color preference.
        conflict = player_1.color_preference.side.conflicts(player_2.color_preference.side)
        weight |= int(not conflict)

        return weight
