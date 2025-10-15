from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C19(QualityCriterion):
    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        if not bracket.two_rounds_played:
            return 0
        return bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        weight = DynamicUint(zero)

        if player_2.role == PlayerRole.LOWER or not bracket.two_rounds_played:
            return weight

        double = (player_2.float_2 == Float.UP) and (player_1.points > player_2.points)
        difference = player_1.points - bracket.min_bracket_score + 10
        weight -= (zero | int(double)) << bracket.score_difference_bit_dict[difference]

        return weight
