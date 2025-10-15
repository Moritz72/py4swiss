from py4swiss.engines.dutch.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dutch.player import Player


class C2(AbsoluteCriterion):
    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """
        Evaluates whether a player receiving a pairing-allocated bye complies with the absolute
        criterion C.2.

        According to FIDE Rules:
            "A player who has already received a pairing-allocated bye, or has already scored a
            (forfeit) win due to an opponent not appearing in time, shall not receive the
            pairing-allocated bye (see C.04.1.d)."

        This method determines if the given player receiving a bye is valid under that rule. The
        second argument is unused.
        """
        return not player_1.bye_received
