from py4swiss.engines.common import ColorPreferenceStrength
from py4swiss.engines.dutch.player_info import PlayerInfo
from py4swiss.matching_computer import ComputerDutchValidity


class ValidityMatcher:
    def __init__(self, player_list: list[PlayerInfo]) -> None:
        self.player_list: list[PlayerInfo] = player_list
        self.num: int = len(player_list)
        self.computer: ComputerDutchValidity = ComputerDutchValidity(len(self), 1)

        self.index_dict: dict[PlayerInfo, int] = {player: i for i, player in enumerate(self.player_list)}
        self.index_dict_reverse: dict[int, PlayerInfo] = {i: player for i, player in enumerate(self.player_list)}

        for _ in range(len(self)):
            self.computer.add_vertex()

        for i, player_1 in enumerate(self.player_list):
            for j, player_2 in enumerate(self.player_list[i + 1:]):
                self.computer.set_edge_weight(i, i + j + 1, int(self.is_allowed_pairing(player_1, player_2)))

        if self.num % 2 == 1:
            for i, player in enumerate(self.player_list):
                self.computer.set_edge_weight(i, self.num, not int(player.bye_received))

    def __len__(self) -> int:
        return self.num + (self.num % 2)

    @staticmethod
    def is_allowed_pairing(player_1: PlayerInfo, player_2: PlayerInfo) -> bool:
        # C.1
        if player_1.number in player_2.opponents:
            return False

        # C.3
        topscorer = player_1.top_scorer or player_2.top_scorer
        same_preference = player_1.color_preference.side == player_2.color_preference.side
        absolute_1 = player_1.color_preference.strength == ColorPreferenceStrength.ABSOLUTE
        absolute_2 = player_2.color_preference.strength == ColorPreferenceStrength.ABSOLUTE
        if not topscorer and same_preference and absolute_1 and absolute_2:
            return False

        return True

    def is_valid_matching(self) -> bool:
        self.computer.compute_matching()
        return all(i != j for i, j in enumerate(self.computer.get_matching()))

    def finalize_match(self, player: PlayerInfo, opponent: PlayerInfo) -> None:
        i = self.index_dict[player]
        j = self.index_dict[opponent]
        for k in range(len(self)):
            self.computer.set_edge_weight(i, k, 0)
            self.computer.set_edge_weight(j, k, 0)
        self.computer.set_edge_weight(i, j, 1)
