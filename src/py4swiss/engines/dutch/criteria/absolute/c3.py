from py4swiss.engines.common import ColorPreferenceStrength
from py4swiss.engines.dutch.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dutch.player import Player


class C3(AbsoluteCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """
        Evaluates whether a pairing between two players complies with the absolute criterion C.3.

        According to FIDE Rules:
            "Non-topscorers (see A.7) with the same absolute colour preference (see A6.a)
            shall not meet (see C.04.1.f and C.04.1.g)."

        This method determines if a pairing between the given players is valid under that rule.
        The pairing is considered valid if any of the following conditions hold:
            - At least one of the players is a top scorer
            - The players do not share the same colour preference side
            - Either player does not have an absolute colour preference
        """
        topscorer = player_1.top_scorer or player_2.top_scorer
        same_preference = player_1.color_preference.side == player_2.color_preference.side
        absolute_1 = player_1.color_preference.strength == ColorPreferenceStrength.ABSOLUTE
        absolute_2 = player_2.color_preference.strength == ColorPreferenceStrength.ABSOLUTE
        return topscorer or not same_preference or not absolute_1 or not absolute_2
