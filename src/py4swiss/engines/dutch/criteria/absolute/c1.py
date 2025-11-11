from py4swiss.engines.dutch.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dutch.player import Player


class C1(AbsoluteCriterion):
    """
    Implementation of the absolute criterion C.1.

    FIDE handbook: "C Pairing Criteria | Absolute Criteria | C.1"
    see C.04.1.b (Two players shall not play against each other more than once)
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """Check whether the given players have already played each other in previous rounds."""
        return player_1.id not in player_2.opponents
