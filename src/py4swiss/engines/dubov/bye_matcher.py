from py4swiss.engines.common import PairingError
from py4swiss.engines.dubov.criteria.absolute import C1, C2, C3
from py4swiss.engines.dubov.player import Player
from py4swiss.matching_computer import ComputerDutchValidity


class ByeMatcher:
    """A class used to determine which player should receive the pairings allocated bye."""

    def __init__(self, players: list[Player], forbidden_pairs: set[tuple[int, int]]) -> None:
        """
        Set up a new matching computer.

        The included graph contains exactly one vertex for each player as well as one for the pairing-allocated bye and
        edges with weights between them depending on whether they are allowed to be paired with each other or not.
        """
        self._players: list[Player] = players
        self._forbidden_pairs: set[tuple[int, int]] = forbidden_pairs

        bye_weights, max_weight = self._get_bye_weights()
        self._bye_weights: list[int] = bye_weights
        self._max_weight: int = max_weight

        self._len: int = len(players)
        self._computer: ComputerDutchValidity = ComputerDutchValidity(self._len + 1, self._max_weight)
        self._index_dict_reverse: dict[int, Player] = dict(enumerate(self._players))

        self._set_up_computer()

    def _get_bye_weights(self) -> tuple[list[int], int]:
        """Return weights to determine the best choice for the pairing-allocated bye."""
        points_list = sorted({player.points_with_acceleration for player in self._players}, reverse=True)
        games_list = sorted({len(player.opponents) for player in self._players}, reverse=True)

        points_upper_bound = len(points_list) + 1
        games_upper_bound = len(games_list) + 1

        # Choose the weights between players and the pairing-allocated bye according to the bye preferences. 3.1.5 is
        # not yet considered here.

        # FIDE handbook: "3.1 Pairing-Allocated-Bye Assignment"
        # The pairing-allocated-bye is assigned to the player who:
        # 3.1.1 has neither received a pairing-allocated-bye, nor scored a (forfeit) win in the previous rounds (see
        #       [C2], Article 2.1.2)
        # 3.1.2 allows a complete pairing of all the remaining players (see [C4], Article 2.2.1)
        # 3.1.3 has the lowest score
        # 3.1.4 has played the highest number of games
        # 3.1.5 has the largest TPN (see Article 1.2)

        bye_weights = [
            (
                (points_list.index(player.points) + 1) * games_upper_bound + games_list.index(len(player.opponents)) + 1
                if C2.evaluate(player, player)
                else 0
            )
            for player in self._players
        ]

        return bye_weights, points_upper_bound * games_upper_bound

    def _is_allowed_pair(self, player_1: Player, player_2: Player) -> bool:
        """Check whether the given players are allowed to be paired together."""
        # Not yet covered by test
        if bool({(player_1.id, player_2.id), (player_2.id, player_1.id)} & self._forbidden_pairs):  # pragma: no cover
            return False
        return C1.evaluate(player_1, player_2) and C3.evaluate(player_1, player_2)

    def _set_up_computer(self) -> None:
        """
        Configure the matching computer by setting up vertices and edge weights.

        Each vertex represents a player with the very last one representing the pairing-allocated bye.
        """
        for _ in range(self._len + 1):
            self._computer.add_vertex()

        # Maximize the number of pairs.
        for i, player_1 in enumerate(self._players):
            for j, player_2 in enumerate(self._players[i + 1 :]):
                if self._is_allowed_pair(player_1, player_2):
                    self._computer.set_edge_weight(i, i + j + 1, self._max_weight)

        for i in range(len(self._players)):
            self._computer.set_edge_weight(i, self._len, self._bye_weights[i])

    def get_bye(self) -> Player:
        """
        Choose the player to receive the pairing allocated bye.

        However, if the round pairing can not be completed, return None.
        """
        self._computer.compute_matching()

        # Check whether the round pairing can be completed.
        if not all(i != j for i, j in enumerate(self._computer.get_matching())):
            error_message = "Round can not be paired."
            raise PairingError(error_message)

        # Incentivize giving the pairing-allocated bye to the lowest ranked player possible. See the "BracketPairer"
        # class for comparison.
        for i in range(self._len - 1, -1, -1):
            if self._bye_weights[i] == 0:
                continue

            self._computer.set_edge_weight(i, self._len, self._bye_weights[i] + 1)
            self._computer.compute_matching()
            matching = self._computer.get_matching()

            if matching[i] == self._len:
                return self._index_dict_reverse[i]

            self._computer.set_edge_weight(i, self._len, self._bye_weights[i])

        error_message = "Unreachable code reached"  # pragma: no cover
        raise AssertionError(error_message)  # pragma: no cover
