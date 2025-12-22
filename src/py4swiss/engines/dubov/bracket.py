from py4swiss.engines.dubov.player import Player, PlayerRole


class Bracket:
    """
    A class for keeping and updating the current bracket.

    FIDE handbook: "1.3 Scoregroups and Pairing Brackets"
    1.3.1 A scoregroup is composed of all the players with the same score.
    1.3.2 A (pairing) bracket is a group of players to be paired. It is composed of players coming from the same
          scoregroup (called resident players) and (possibly) of players coming from lower scoregroups (called
          upfloaters).
    """

    def __init__(self, players: list[Player]) -> None:
        """Initialize a new bracket."""
        self.players: list[Player] = players

        self._assign_roles()

    def _assign_roles(self) -> None:
        """Assign roles to the players for the current bracket."""
        if self.is_finished():
            return

        max_points = max(player.points_with_acceleration for player in self.players)

        for player in self.players:
            if player.points_with_acceleration == max_points:
                player.role = PlayerRole.RESIDENT
            else:
                player.role = PlayerRole.LOWER

    def is_finished(self) -> bool:
        """Check whether all brackets have been exhausted."""
        return len(self.players) <= 1

    def apply_pairings(self, player_pairs: list[tuple[Player, Player]]) -> None:
        """Remove the paired players and update the current bracket accordingly."""
        paired_players = {player for pair in player_pairs for player in pair}

        self.players = [player for player in self.players if player not in paired_players]
        self._assign_roles()
