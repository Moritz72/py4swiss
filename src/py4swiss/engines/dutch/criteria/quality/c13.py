from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C13(QualityCriterion):
    """
    Implementation of the quality criterion C.13.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.13"
    minimize the number of players who receive the same upfloat as the previous round.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        if not bracket.two_rounds_played:
            return 0
        # See C.12.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight of 1, if neither player both received an upfloat in the previous round and will also receive one
        this round, assuming the players are paired with each other, else 0. However, if one of the given players is
        neither an MDP nor a resident, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER or not bracket.two_rounds_played:
            return weight

        # The lower ranked player has the same as or fewer points than the higher ranked player. Thus, the latter will
        # never receive an upfloat when paired with a lower ranked player. Since, unlike in C.12, unpaired players can
        # never upfloat, such players can be ignored. Thus, with this choice of weigh, the maximum round pairing weight
        # sum will minimize the number of paired players that receive the same upfloat as the previous round.
        player_1_more_points = player_1.points_with_acceleration > player_2.points_with_acceleration
        double_float = (player_2.float_1 == Float.UP) and player_1_more_points
        weight |= int(not double_float)

        return weight
