from itertools import groupby

from py4swiss.engines.dutch.bracket.bracket import Bracket
from py4swiss.engines.dutch.player import Player, PlayerRole


class Brackets:
    def __init__(self, players: list[Player], round_number: int) -> None:
        self._brackets: list[list[Player]] = [list(group) for score, group in groupby(players, key=lambda p: p.points)]
        self._round_number: int = round_number

        self._index: int = 0
        self._collapsed: bool = False
        self._mdp_list: list[Player] = []

        self._assign_roles()

    def _get_resident_list(self) -> list[Player]:
        if self._index >= len(self._brackets):
            return []
        return self._brackets[self._index]

    def _get_lower_list(self) -> list[Player]:
        if self._index + 1 >= len(self._brackets):
            return []
        return self._brackets[self._index + 1]

    def _assign_roles(self) -> None:
        for mdp in self._mdp_list:
            mdp.role = PlayerRole.MDP

        for resident in self._get_resident_list():
            resident.role = PlayerRole.RESIDENT

        for lower in self._get_lower_list():
            lower.role = PlayerRole.LOWER

    def is_finished(self) -> bool:
        return self._index == len(self._brackets)

    def get_current_bracket(self) -> Bracket:
        return Bracket.from_data(
            self._mdp_list,
            self._get_resident_list(),
            self._get_lower_list(),
            self._round_number,
            self._collapsed
        )

    def apply_bracket_pairings(self, player_pairs: list[tuple[Player, Player]]) -> None:
        paired_players = {player for pair in player_pairs for player in pair}
        candidates = self._mdp_list + self._get_resident_list()

        self._mdp_list = [player for player in candidates if player not in paired_players]
        self._index += 1

        self._assign_roles()

    def collapse(self) -> None:
        collapsed_last_bracket = [player for bracket in self._brackets[self._index + 1:] for player in bracket]

        self._brackets = self._brackets[:self._index + 1] + [collapsed_last_bracket]
        self._collapsed = True

        self._assign_roles()
