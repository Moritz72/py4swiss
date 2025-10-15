from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C6(QualityCriterion):
    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        return bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        weight = DynamicUint(zero)

        if player_2.role == PlayerRole.LOWER:
            return weight

        difference_1 = player_1.points - bracket.min_bracket_score + 10
        difference_2 = player_2.points - bracket.min_bracket_score + 10
        difference_3 = player_1.points - player_2.points

        weight += (zero | 1) << bracket.score_difference_bit_dict[difference_1]
        weight += (zero | 1) << bracket.score_difference_bit_dict[difference_2]
        weight -= (zero | 1) << bracket.score_difference_bit_dict.get(difference_3, 0)

        return weight
