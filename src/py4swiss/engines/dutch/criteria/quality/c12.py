from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C12(QualityCriterion):
    """
    Implementation of the quality criterion C.12.

    FIDE handbook: "C Pairing Criteria | Quality Criteria | C.12"
    minimize the number of players who receive the same downfloat as the previous round.
    """

    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        """Return the number of bits needed to represent all residents in the given bracket."""
        if not bracket.one_round_played:
            return 0
        # Since the weight for each pair will be at most 2, the number of residents in the bracket will always be
        # greater than the sum of all weights.
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        """
        Return a weight of 2 - n, where n is the number of the given players who received a downfloat in the previous
        round but will not receive one this round, assuming the players are paired with each other. However, if one of
        the given players is neither an MDP nor a resident, then a weight of 0 will be returned.
        """
        weight = DynamicUint(zero)

        # Only pairings between MDPs or residents count as pairs.
        if player_2.role == PlayerRole.LOWER or not bracket.one_round_played:
            return weight

        # The lower ranked player has the same as or fewer points than the higher ranked player. Thus, the former will
        # never receive a downfloat when paired with a higher ranked player. Note also that unpaired players will be
        # MDPs in the following bracket or receive the pairing-allocated bye and thus downfloat. Thus, it is necessary
        # to count exactly the number of residents in given bracket who received a downloat in the previous round, but
        # will not receive one in this round, in order to get the maximum round pairing weight sum to minimize the
        # number of paired players that receive the same downfloat as the previous round.
        player_2_equal_or_more_points = player_1.points_with_acceleration <= player_2.points_with_acceleration
        prevented_double_float_1 = (player_1.float_1 == Float.DOWN) and player_2_equal_or_more_points
        prevented_double_float_2 = player_2.float_1 == Float.DOWN
        weight |= int(prevented_double_float_1) + int(prevented_double_float_2)

        return weight
