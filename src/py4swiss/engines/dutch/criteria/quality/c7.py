from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C7(QualityCriterion):
    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        if bracket.penultimate_pairing_bracket or bracket.last_pairing_bracket:
            return 0
        return bracket.low_bracket_bits + bracket.score_difference_total_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        weight = DynamicUint(zero)

        if bracket.penultimate_pairing_bracket or bracket.last_pairing_bracket:
            return weight

        weight |= int(player_2.role == PlayerRole.LOWER)
        weight <<= bracket.score_difference_total_bits

        if not player_1.role == PlayerRole.LOWER:
            difference = player_1.points - bracket.min_bracket_score + 10
            weight += (zero | 1) << bracket.score_difference_bit_dict[difference]

        if not player_2.role == PlayerRole.LOWER:
            difference = player_2.points - bracket.min_bracket_score + 10
            weight += (zero | 1) << bracket.score_difference_bit_dict[difference]

        return weight
