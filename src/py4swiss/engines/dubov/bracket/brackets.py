from py4swiss.engines.dubov.bracket.bracket import Bracket
from py4swiss.engines.dubov.player import Player, PlayerRole


class Brackets:
    """
    A class for keeping and updating score groups as well as determining the current bracket.

    FIDE handbook: "1.3 Scoregroups and Pairing Brackets"
    1.3.1 A scoregroup is composed of all the players with the same score.
    1.3.2 A (pairing) bracket is a group of players to be paired. It is composed of players coming from the same
          scoregroup (called resident players) and (possibly) of players coming from lower scoregroups (called
          upfloaters).
    """

    def __init__(self, players: list[Player], round_number: int, number_of_rounds: int) -> None:
        """Initialize new brackets."""
        self._player_list: list[Player] = players
        self._round_number: int = round_number
        self._number_of_rounds: int = number_of_rounds

        self._assign_roles()

    def _assign_roles(self) -> None:
        """Assign roles to the players for the current bracket."""
        if self.is_finished():
            return

        max_points = max(player.points_with_acceleration for player in self._player_list)

        for player in self._player_list:
            if player.points_with_acceleration == max_points:
                player.role = PlayerRole.RESIDENT
            else:
                player.role = PlayerRole.LOWER

    def get_current_bracket(self) -> Bracket:
        """Return the current bracket."""
        return Bracket.from_data(self._player_list, self._round_number, self._number_of_rounds)

    def is_finished(self) -> bool:
        """Check whether all brackets have been exhausted."""
        return len(self._player_list) <= 1

    def apply_bracket_pairings(self, player_pairs: list[tuple[Player, Player]]) -> None:
        """Remove the paired players and update the current bracket accordingly."""
        paired_players = {player for pair in player_pairs for player in pair}

        self._player_list = [player for player in self._player_list if player not in paired_players]
        self._assign_roles()
