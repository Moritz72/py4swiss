from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dubov.bracket import Bracket
from py4swiss.engines.dubov.criteria.abstract import QualityCriterion
from py4swiss.engines.dubov.player import Player, PlayerRole


class C7(QualityCriterion):
    """
    Implementation of the quality criterion C.7.

    FIDE handbook: "2. Pairing Criteria | 2.3 Quality Criteria | 2.3.3 [C.7]"
    Minimise the number of players who do not get their colour preference.
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

        Case 1: None of the given players are residents
        Case 2: Both players have the same color preference side
        """
        weight = DynamicUint(zero)

        # Only pairings involving residents count as pairs.
        if player_1.role == PlayerRole.LOWER:
            return weight

        # There will be a player in a pair who does not get their color preference, if and only if both players in the
        # pair have the same color preference side. Furthermore, at least one player in each pair will get their color
        # preference. Thus, with this choice of weight, the maximum round pairing weight sum will minimize the number of
        # paired players that do not get their color preference.
        conflict = player_1.color_preference.side.conflicts(player_2.color_preference.side)
        weight |= int(not conflict)

        return weight
