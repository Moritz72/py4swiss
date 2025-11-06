from py4swiss.engines.dutch.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dutch.player import Player


class C2(AbsoluteCriterion):
    """
    Implementation of the absolute criterion C.2.

    FIDE handbook: "C Pairing Criteria | Absolute Criteria | C.2"
    see C.04.1.d (A player who has already received a pairing-allocated bye, or has already scored a (forfeit) win due
    to an opponent not appearing in time, shall not receive the pairing-allocated bye).
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """Check whether the given player as received a bye or forfeit win. The second argument is unused."""
        return not player_1.bye_received
