from py4swiss.engines.dubov.criteria.abstract import AbsoluteCriterion
from py4swiss.engines.dubov.player import Player


class C2(AbsoluteCriterion):
    """
    Implementation of the absolute criterion C.2.

    FIDE handbook: "2. Pairing Criteria | 2.1 Absolute Criteria | [C2]"
    See the Basic Rules for Swiss, Article 4 (A participant who has already received a pairing-allocated bye, or has
    already scored in one single round, without playing, as many points as rewarded for a win, shall not receive the
    pairing-allocated bye).
    """

    @classmethod
    def evaluate(cls, player_1: Player, player_2: Player) -> bool:
        """Check whether the given player has received a pairing-allocated bye or has similar unplayed rounds."""
        return not player_1.bye_received
