from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket import Bracket
from py4swiss.engines.common import ColorPreferenceStrength
from py4swiss.engines.dutch.criteria.abstract import QualityCriterion
from py4swiss.engines.dutch.player import Player, PlayerRole


class C11(QualityCriterion):
    @classmethod
    def get_shift(cls, bracket: Bracket) -> int:
        return bracket.bracket_bits

    @classmethod
    def get_weight(cls, player_1: Player, player_2: Player, zero: DynamicUint, bracket: Bracket) -> DynamicUint:
        weight = DynamicUint(zero)

        if player_2.role == PlayerRole.LOWER:
            return weight

        strong = all(p.color_preference.strength >= ColorPreferenceStrength.STRONG for p in (player_1, player_2))
        conflict = player_1.color_preference.side == player_2.color_preference.side
        weight |= int(not (strong and conflict))

        return weight
