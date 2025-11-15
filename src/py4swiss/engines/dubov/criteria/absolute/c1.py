from py4swiss.engines.dubov.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dubov.player import Player


class C1(AbsoluteCriterion):
    """
    Implementation of the absolute criterion C.1.

    FIDE handbook: "2. Pairing Criteria | 2.1 Absolute Criteria | 2.1.1 [C1]"
    See the Basic Rules for Swiss, Article 2 (Two participants shall not play against each other more than once).
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """Check whether the given players have already played each other in previous rounds."""
        return player_1.id not in player_2.opponents
