from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import Float
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C14(QualityCriterion):
    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        if not bracket.one_round_played:
            return 0
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        weight = DynamicUint(zero)

        if player_2.role == PlayerRole.LOWER or not bracket.one_round_played:
            return weight

        prevented_double_float_1 = (player_1.float_2 == Float.DOWN) and (player_1.points <= player_2.points)
        prevented_double_float_2 = player_2.float_2 == Float.DOWN
        weight |= int(prevented_double_float_1) + int(prevented_double_float_2)

        return weight
