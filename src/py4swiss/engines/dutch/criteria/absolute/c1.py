from py4swiss.engines.dutch.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dutch.player import Player


class C1(AbsoluteCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """
        Evaluates whether a pairing between two players complies with the absolute criterion C.1.

        According to the FIDE Rules:
            "Two players shall not play against each other more than once." (see C.04.1.b)

        This method checks whether `the given players have already played each other in previous
        rounds. If they have not met before, the pairing is considered valid.
        """
        return player_1.number not in player_2.opponents
