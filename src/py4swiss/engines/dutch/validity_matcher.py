from py4swiss.engines.dutch.criteria.absolute import C1, C2, C3
from py4swiss.engines.dutch.player import Player
from py4swiss.matching_computer import ComputerDutchValidity


class ValidityMatcher:
    """A class used to determine whether the current choice of pairings allows completion of the round-pairing."""

    def __init__(self, players: list[Player], forbidden_pairs: set[tuple[int, int]]) -> None:
        """
        Set up a new matching computer.

        The included graph contains exactly one vertex for each player and edges with weights between them depending on
        whether they are allowed to be paired with each other or not.
        """
        self._players: list[Player] = players
        self._forbidden_pairs: set[tuple[int, int]] = forbidden_pairs

        self._len: int = len(players) + len(players) % 2
        self._computer: ComputerDutchValidity = ComputerDutchValidity(self._len, 1)
        self._index_dict: dict[Player, int] = {player: i for i, player in enumerate(self._players)}

        self._set_up_computer()

    def _set_up_computer(self) -> None:
        """
        Configure the matching computer by setting up vertices and edge weights.

        Each vertex represents a player (and potentially an extra one for a bye if needed).
        Edge weights are determined by the validity of pairings according to the absolute criteria C.1, C.2, and C.3:
            - 1 if the pairing between two players is allowed
            - 0 if it violates any absolute criteria
        """
        for _ in range(self._len):
            self._computer.add_vertex()

        for i, player_1 in enumerate(self._players):
            for j, player_2 in enumerate(self._players[i + 1 :]):
                self._computer.set_edge_weight(i, i + j + 1, int(self.is_allowed_pair(player_1, player_2)))

        if len(self._players) % 2 == 1:
            for i, player in enumerate(self._players):
                allowed = C2.evaluate(player, player)
                self._computer.set_edge_weight(i, len(self._players), int(allowed))

    def is_allowed_pair(self, player_1: Player, player_2: Player) -> bool:
        """Check whether the given players are allowed to be paired together."""
        if bool({(player_1.id, player_2.id), (player_2.id, player_1.id)} & self._forbidden_pairs):
            return False
        return C1.evaluate(player_1, player_2) and C3.evaluate(player_1, player_2)

    def finalize_match(self, player_1: Player, player_2: Player) -> None:
        """Finalize the fact that the given players will be paired with one another."""
        i = self._index_dict[player_1]
        j = self._index_dict[player_2]

        for k in range(self._len):
            self._computer.set_edge_weight(i, k, 0)
            self._computer.set_edge_weight(j, k, 0)

        self._computer.set_edge_weight(i, j, 1)

    def is_valid_matching(self) -> bool:
        """
        Check whether the current edge weights allow for a full pairing of all players.

        This means that the absolute criteria C.1, C.2, and C.3 need to be adhered to whilst still pairing each player
        to exactly one other player.
        """
        self._computer.compute_matching()
        return all(i != j for i, j in enumerate(self._computer.get_matching()))
