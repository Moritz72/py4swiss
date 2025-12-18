from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import PairingError
from py4swiss.engines.dubov.bracket.bracket import Bracket
from py4swiss.engines.dubov.criteria import QUALITY_CRITERIA
from py4swiss.engines.dubov.criteria.absolute import C1, C3
from py4swiss.engines.dubov.player import Player
from py4swiss.matching_computer import ComputerDutchOptimality


class BracketMatcher:
    """A class aiding in the pairing process for a bracket."""

    def __init__(self, bracket: Bracket, forbidden_pairs: set[tuple[int, int]]) -> None:
        """
        Set up a new matching computer.

        The included graph contains exactly one vertex for each player and edges with weights between according to the
        absolute and quality criteria.
        """
        self._bracket: Bracket = bracket
        self._forbidden_pairs: set[tuple[int, int]] = forbidden_pairs

        self._player_list: list[Player] = bracket.resident_list + bracket.lower_list

        self._max_weight: DynamicUint = self._get_max_weight()
        self._zero_weight: DynamicUint = self._max_weight & 0

        self._len: int = len(self._player_list)
        self._index_dict_reverse: dict[int, Player] = dict(enumerate(self._player_list))
        self._index_dict: dict[Player, int] = {player: i for i, player in self._index_dict_reverse.items()}

        self._computer: ComputerDutchOptimality = ComputerDutchOptimality(self._len, self._max_weight)
        self._weights: list[list[DynamicUint]] = [[self._zero_weight] * self._len for _ in range(self._len)]

        self.matching: dict[Player, Player] = {}
        self._set_up_computer()
        self.update_matching()

        # Check whether the round pairing can be completed.
        if not all(i != j for i, j in enumerate(self._computer.get_matching())):
            error_message = "Round can not be paired."
            raise PairingError(error_message)

    def _get_index(self, player: Player) -> int:
        """Return the vertex index of the given player."""
        return self._index_dict[player]

    def _get_player(self, index: int) -> Player:
        """Return the player for the given vertex index."""
        return self._index_dict_reverse[index]

    def _set_weight(self, i: int, j: int, weight: DynamicUint) -> None:
        """Set the edge weight between the vertices with the given indices to the given weight."""
        self._weights[i][j] = weight
        self._weights[j][i] = weight
        self._computer.set_edge_weight(i, j, weight)

    def _remove_weight(self, i: int, j: int) -> None:
        """Remove the edge between the vertices with the given indices."""
        weight = self._weights[i][j]

        # An edge weight of zero counts as no edge.
        if not bool(weight):
            return

        weight &= 0
        self._computer.set_edge_weight(i, j, weight)

    def _get_max_weight(self) -> DynamicUint:
        """
        Return a weight large enough to hold all quality criteria.

        Additionally, this also includes some space for transpositions.
        """
        weight = DynamicUint(1)

        # Bit for ensuring completion of the round pairing.
        weight.shift_grow(1)

        # Bits for quality criteria.
        for criterion in QUALITY_CRITERIA:
            weight.shift_grow(criterion.get_shift(self._bracket))

        # Bits for transpositions.
        weight.shift_grow(self._bracket.bracket_bits)

        # Margin for the matching routine.
        weight.shift_grow(2)

        # Set all bits to 1.
        weight >>= 1
        weight -= (weight & 0) | 1

        return weight

    def _get_weight(self, player_1: Player, player_2: Player) -> DynamicUint:
        """Return a weight containing all quality criteria."""
        weight = DynamicUint(self._zero_weight)

        # Only players that can be paired with each other according to the absolute criteria get an edge.
        if not self._is_allowed_pair(player_1, player_2):
            return weight

        # Give each edge a weight to maximize the number of matched pairs.
        weight |= 1

        # Add the individual quality criteria weights from most important to least important and shift in order to not
        # overwrite any previously set bits. The shift amount is such that, even for the sum of all weights of a given
        # round pairing, the values of a quality criterion with lower importance can not overflow to parts reserved for
        # a criterion with higher importance.
        for criterion in QUALITY_CRITERIA:
            weight <<= criterion.get_shift(self._bracket)
            weight += criterion.get_weight(player_1, player_2, self._zero_weight, self._bracket)

        # There needs to be free space at the bottom for adding transposition preferences later on.
        weight <<= self._bracket.bracket_bits

        return weight

    def _is_allowed_pair(self, player_1: Player, player_2: Player) -> bool:
        """Check whether the given players are allowed to be paired together."""
        # Not yet covered by test
        if bool({(player_1.id, player_2.id), (player_2.id, player_1.id)} & self._forbidden_pairs):  # pragma: no cover
            return False
        return C1.evaluate(player_1, player_2) and C3.evaluate(player_1, player_2)

    def _set_up_computer(self) -> None:
        """Initialize the graph with a vertex for each player as well as edges with weights between them."""
        for _ in range(self._len):
            self._computer.add_vertex()

        for i, player_1 in enumerate(self._player_list):
            for j, player_2 in enumerate(self._player_list[i + 1 :]):
                weight = self._get_weight(player_1, player_2)
                self._set_weight(i, i + j + 1, weight)

    def add_to_weight(self, player_1: Player, player_2: Player, value: int) -> None:
        """Add the given integer value to the edge weight between the given players."""
        i, j = self._get_index(player_1), self._get_index(player_2)

        # An edge weight of zero counts as no edge.
        if not bool(self._weights[i][j]):
            return

        # Since weights can not be negative, the sign of the given value needs to be taken special care of.
        weight = self._zero_weight | abs(value)
        if value > 0:
            self._set_weight(i, j, self._weights[i][j] + weight)
        else:
            self._set_weight(i, j, self._weights[i][j] - weight)

    def add_to_weights(self, player: Player, player_list: list[Player], value: int, increment: bool = False) -> None:
        """
        Add the given value to each edge weight between the given player and any player in the given list in order.

        The value can optionally be incremented by 1 after each addition.
        """
        for other in player_list:
            self.add_to_weight(player, other, value)
            value += int(increment)

    def remove_weight(self, player_1: Player, player_2: Player) -> None:
        """Remove the edge between the given players."""
        i, j = self._get_index(player_1), self._get_index(player_2)
        self._remove_weight(i, j)

    def remove_weights(self, player: Player, player_list: list[Player]) -> None:
        """Remove each edge between the given player and any player in the given list."""
        for other in player_list:
            self.remove_weight(player, other)

    def update_matching(self) -> None:
        """Compute a new matching efficiently by only considering vertices which were marked as updated."""
        self._computer.compute_matching()
        matching = self._computer.get_matching()

        self.matching = {self._get_player(i): self._get_player(j) for i, j in enumerate(matching)}

    def finalize_match(self, player_1: Player, player_2: Player) -> None:
        """Finalize the fact that the given player are to be paired with one another."""
        i, j = self._get_index(player_1), self._get_index(player_2)

        # Removing all edges between the given players and any other players besides one another will force the matching
        # algorithm to match the given players with each other.
        for k in range(self._len):
            self._remove_weight(i, k)
            self._remove_weight(j, k)
        self._set_weight(i, j, self._max_weight)
