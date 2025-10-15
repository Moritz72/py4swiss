from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.dutch.bracket.bracket import Bracket
from py4swiss.engines.dutch.criteria import QUALITY_CRITERIA
from py4swiss.engines.dutch.criteria.absolute import C1, C3
from py4swiss.engines.dutch.player import Player
from py4swiss.matching_computer import ComputerDutchOptimality


class BracketMatcher:
    def __init__(self, bracket: Bracket) -> None:
        self._player_list: list[Player] = bracket.mdp_list + bracket.resident_list + bracket.lower_list
        self._bracket: Bracket = bracket

        self._max_weight: DynamicUint = self._get_max_weight()
        self._zero_weight: DynamicUint = self._max_weight & 0

        self._len: int = len(self._player_list)
        self._index_dict: dict[Player, int] = {player: i for i, player in enumerate(self._player_list)}
        self._index_dict_reverse: dict[int, Player] = {i: player for i, player in enumerate(self._player_list)}

        self._computer: ComputerDutchOptimality = ComputerDutchOptimality(self._len, self._max_weight)
        self._weights: list[list[DynamicUint]] = [[self._zero_weight] * self._len for _ in range(self._len)]

        self.matching: dict[Player, Player] = {}
        self._set_up_computer()
        self.update_matching()

    def _get_index(self, player: Player) -> int:
        return self._index_dict[player]

    def _get_player(self, index: int) -> Player:
        return self._index_dict_reverse[index]

    def _set_weight(self, i: int, j: int, weight: DynamicUint) -> None:
        self._weights[i][j] = weight
        self._weights[j][i] = weight
        self._computer.set_edge_weight(i, j, weight)

    def _remove_weight(self, i: int, j: int) -> None:
        weight = self._weights[i][j]
        if not bool(weight):
            return

        weight &= 0
        self._computer.set_edge_weight(i, j, weight)

    def _get_max_weight(self) -> DynamicUint:
        weight = DynamicUint(1)

        weight.shift_grow(2)

        for criterion in QUALITY_CRITERIA:
            weight.shift_grow(criterion.get_shift(self._bracket))

        weight.shift_grow(3 * self._bracket.bracket_bits)

        weight.shift_grow(2)
        weight >>= 1
        weight -= (weight & 0) | 1

        return weight

    def _get_weight(self, player_1: Player, player_2: Player) -> DynamicUint:
        weight = DynamicUint(self._zero_weight)

        if not C1.evaluate(player_1, player_2) or not C3.evaluate(player_1, player_2):
            return weight

        if self._bracket.penultimate_pairing_bracket or self._bracket.last_pairing_bracket:
            weight |= 1 + player_1.bye_received + player_2.bye_received

        for criterion in QUALITY_CRITERIA:
            weight <<= criterion.get_shift(self._bracket)
            weight += criterion.get_weight(player_1, player_2, self._zero_weight, self._bracket)

        weight <<= 3 * self._bracket.bracket_bits + 1
        return weight

    def _set_up_computer(self) -> None:
        for _ in range(self._len):
            self._computer.add_vertex()

        for i, player_1 in enumerate(self._player_list):
            for j, player_2 in enumerate(self._player_list[i + 1:]):
                weight = self._get_weight(player_1, player_2)
                self._set_weight(i, i + j + 1, weight)

    def add_to_weight(self, player_1: Player, player_2: Player, value: int) -> None:
        i, j = self._get_index(player_1), self._get_index(player_2)
        if not bool(self._weights[i][j]):
            return

        weight = self._zero_weight | abs(value)
        if value > 0:
            self._set_weight(i, j, self._weights[i][j] + weight)
        else:
            self._set_weight(i, j, self._weights[i][j] - weight)

    def add_to_weights(self, player: Player, player_list: list[Player], value: int, increment: bool = False) -> None:
        for other in player_list:
            self.add_to_weight(player, other, value)
            value += int(increment)

    def remove_weight(self, player_1: Player, player_2: Player) -> None:
        i, j = self._get_index(player_1), self._get_index(player_2)
        self._remove_weight(i, j)

    def remove_weights(self, player: Player, player_list: list[Player]) -> None:
        for other in player_list:
            self.remove_weight(player, other)

    def update_matching(self) -> None:
        self._computer.compute_matching()
        matching = self._computer.get_matching()

        self.matching = {self._get_player(i): self._get_player(j) for i, j in enumerate(matching)}

    def finalize_match(self, player_1: Player, player_2: Player) -> None:
        i, j = self._get_index(player_1), self._get_index(player_2)

        for k in range(self._len):
            self._remove_weight(i, k)
            self._remove_weight(j, k)

        self._set_weight(i, j, self._max_weight)
