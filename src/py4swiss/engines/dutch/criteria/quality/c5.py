from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C5(QualityCriterion):
    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        weight = DynamicUint(zero)

        weight |= int(not player_2.role == PlayerRole.LOWER)

        return weight
