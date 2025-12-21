from collections.abc import Iterable

from py4swiss.engines.burstein.player import Player, PlayerRole


class Bracket:
    """
    A class for keeping and updating the current bracket.

    FIDE handbook: "1.2 Scoregroups and Pairing Brackets"
    1.2.1 A scoregroup is composed of all the players with the same score.
    1.2.2 A (pairing) bracket is a group of players to be paired. It is composed of players coming from a scoregroup
          (called resident players) and (possibly) of players who remained unpaired after the pairing of the previous
          bracket (called incoming floaters).
    """

    def __init__(self, players: list[Player]) -> None:
        """Initialize a new bracket."""
        self.players: list[Player] = players
        self._resident_score: int = 0

        self._update_resident_score(initial=True)
        self._assign_roles()

    @staticmethod
    def _get_maximum_with_bound(integers: Iterable[int], bound: int) -> int:
        """Get the largest element of the given integers that is lower than the given bound."""
        return max((integer for integer in integers if integer < bound), default=0)

    def _update_resident_score(self, initial: bool = False) -> None:
        """Update the resident score for the current bracket."""
        scores = {player.points_with_acceleration for player in self.players}

        if initial:
            lower_score = sorted(scores, reverse=True)[0]
        else:
            lower_score = self._get_maximum_with_bound(scores, self._resident_score)

        self._resident_score = lower_score

    def _assign_roles(self) -> None:
        """Assign roles to the players for the current bracket."""
        if self.is_finished():
            return

        scores = {player.points_with_acceleration for player in self.players}
        lower_score = self._get_maximum_with_bound(scores, self._resident_score)

        for player in self.players:
            if player.points_with_acceleration >= self._resident_score:
                player.role = PlayerRole.RESIDENT
            elif player.points_with_acceleration == lower_score:
                player.role = PlayerRole.LOWER
            else:
                player.role = PlayerRole.NONE

    def is_finished(self) -> bool:
        """Check whether all brackets have been exhausted."""
        return len(self.players) <= 1

    def apply_pairings(self, player_pairs: list[tuple[Player, Player]]) -> None:
        """Remove the paired players and update the current bracket accordingly."""
        paired_players = {player for pair in player_pairs for player in pair}

        self.players = [player for player in self.players if player not in paired_players]
        self._update_resident_score()
        self._assign_roles()
