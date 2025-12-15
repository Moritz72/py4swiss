from itertools import groupby

from py4swiss.engines.dutch.bracket.bracket import Bracket
from py4swiss.engines.dutch.player import Player, PlayerRole


class Brackets:
    """
    A class for keeping and updating score groups as well as determining the current bracket.

    FIDE handbook: "A.3 Scoregroups and pairing brackets"
    A scoregroup is normally composed of (all) the players with the same score. The only exception is the special
    "collapsed" scoregroup defined in A.9.
    A (pairing) bracket is a group of players to be paired. It is composed of players coming from one same scoregroup
    (called resident players) and of players who remained unpaired after the pairing of the previous bracket.
    """

    def __init__(self, players: list[Player], round_number: int) -> None:
        """Initialize new brackets."""
        self._brackets: list[list[Player]] = [
            list(group) for score, group in groupby(players, key=lambda p: p.points_with_acceleration)
        ]
        self._round_number: int = round_number

        self._index: int = 0
        self._collapsed: bool = False
        self._mdp_list: list[Player] = []

        self._assign_roles()

    def _get_resident_list(self) -> list[Player]:
        """Return the residents of the current bracket."""
        if self._index >= len(self._brackets):
            return []
        return self._brackets[self._index]

    def _get_lower_list(self) -> list[Player]:
        """Return the residents of the next bracket."""
        if self._index + 1 >= len(self._brackets):
            return []
        return self._brackets[self._index + 1]

    def _assign_roles(self) -> None:
        """Assign roles to the relevant player for the current bracket."""
        for mdp in self._mdp_list:
            mdp.role = PlayerRole.MDP

        for resident in self._get_resident_list():
            resident.role = PlayerRole.RESIDENT

        for lower in self._get_lower_list():
            lower.role = PlayerRole.LOWER

    def is_finished(self) -> bool:
        """Check whether all brackets have been exhausted."""
        return self._index == len(self._brackets)

    def get_current_bracket(self) -> Bracket:
        """Return the current bracket."""
        return Bracket.from_data(
            self._mdp_list, self._get_resident_list(), self._get_lower_list(), self._round_number, self._collapsed
        )

    def apply_bracket_pairings(self, player_pairs: list[tuple[Player, Player]]) -> None:
        """Remove the paired players and update the current bracket accordingly."""
        paired_players = {player for pair in player_pairs for player in pair}
        candidates = self._mdp_list + self._get_resident_list()

        # Unpaired players from the current bracket will be MDPs in the next bracket.
        self._mdp_list = [player for player in candidates if player not in paired_players]
        self._index += 1

        self._assign_roles()

    def collapse(self) -> None:
        """Mark the current bracket as the PPB and collapse the last bracket."""
        # FIDE handbook: "A.9 Round-Pairing Outlook"
        # However, if, during this process, the downfloaters (possibly none) produced by the bracket just paired,
        # together with all the remaining players, do not allow the completion of the round-pairing, a different
        # processing route is followed. The last paired bracket is called Penultimate Pairing Bracket (PPB). The score
        # of its resident players is called the "collapsing" score. All the players with a score lower than the
        # collapsing score constitute the special "collapsed" scoregroup mentioned in A.3.
        collapsed_last_bracket = [player for bracket in self._brackets[self._index + 1 :] for player in bracket]

        self._brackets = [*self._brackets[: self._index + 1], collapsed_last_bracket]
        self._collapsed = True

        self._assign_roles()
