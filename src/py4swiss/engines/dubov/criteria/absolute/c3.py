from py4swiss.engines.common import ColorPreferenceStrength
from py4swiss.engines.dubov.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dubov.player import Player


class C3(AbsoluteCriterion):
    """
    Implementation of the absolute criterion C.3.

    FIDE handbook: "2. Pairing Criteria | 2.1 Absolute Criteria | 2.1.3 [C3]"
    Two players with the same absolute colour preference (see Article 1.6.1) shall not meet (see the Basic Rules for
    Swiss, Articles 6 and 7).
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """Check whether the given players have the same absolute color preference."""
        same_preference = player_1.color_preference.side == player_2.color_preference.side
        absolute_1 = player_1.color_preference.strength == ColorPreferenceStrength.ABSOLUTE
        absolute_2 = player_2.color_preference.strength == ColorPreferenceStrength.ABSOLUTE
        return not same_preference or not absolute_1 or not absolute_2
