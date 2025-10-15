from py4swiss.engines.dutch.bracket.bracket import Bracket
from py4swiss.engines.dutch.bracket.bracket_matcher import BracketMatcher
from py4swiss.engines.dutch.criteria import COLOR_CRITERIA
from py4swiss.engines.dutch.player import Player, PlayerRole
from py4swiss.engines.dutch.validity_matcher import ValidityMatcher


class BracketPairer:
    def __init__(self, state: Bracket, validity_matcher: ValidityMatcher) -> None:
        self._bracket: Bracket = state
        self._validity_matcher: ValidityMatcher = validity_matcher

        self._num: int = len(self._bracket.mdp_list + self._bracket.resident_list + self._bracket.lower_list)
        self._bracket_matcher: BracketMatcher = BracketMatcher(self._bracket)

        self._heterogeneous_s1: list[Player] = []
        self._heterogeneous_s2: list[Player] = []
        self._homogeneous_s1: list[Player] = []
        self._homogeneous_s2: list[Player] = []
        self._exchanges: int = 0

    @staticmethod
    def _get_player_pair(player_1: Player, player_2: Player) -> tuple[Player, Player]:
        if player_1 == player_2:
            return player_1, player_2

        i = 0
        is_white_pair = None

        while is_white_pair is None and i < len(COLOR_CRITERIA):
            is_white_pair = COLOR_CRITERIA[i].evaluate(player_1, player_2)
            i += 1
        assert is_white_pair is not None

        if is_white_pair:
            return player_1, player_2
        return player_2, player_1

    def _get_match_role(self, player: Player) -> PlayerRole:
        return self._bracket_matcher.matching[player].role

    def _has_resident_match(self, player: Player) -> bool:
        return self._get_match_role(player) == PlayerRole.RESIDENT

    def _in_s1(self, player: Player) -> bool:
        return player > self._bracket_matcher.matching[player] and self._get_match_role(player) == PlayerRole.RESIDENT

    def _in_s2(self, player: Player) -> bool:
        return player <= self._bracket_matcher.matching[player] or self._get_match_role(player) == PlayerRole.LOWER

    def determine_heterogeneous_s1(self) -> None:
        for mdp in self._bracket.mdp_list:
            if not self._has_resident_match(mdp):
                self._bracket_matcher.add_to_weights(mdp, self._bracket.resident_list, 1)
                self._bracket_matcher.update_matching()

            if self._has_resident_match(mdp):
                self._heterogeneous_s1.append(mdp)
                self._bracket_matcher.add_to_weights(mdp, self._bracket.resident_list, self._num)

    def determine_heterogeneous_s2(self) -> None:
        for mdp in self._heterogeneous_s1:
            self._bracket_matcher.add_to_weights(mdp, self._bracket.resident_list[::-1], 0, increment=True)
            self._bracket_matcher.update_matching()

            match = self._bracket_matcher.matching[mdp]
            self._heterogeneous_s2.append(match)

            self._bracket_matcher.finalize_match(mdp, match)
            self._validity_matcher.finalize_match(mdp, match)

    def determine_homogeneous_exchanges(self) -> None:
        paired_residents = set(self._heterogeneous_s2)
        remainder = [player for player in self._bracket.resident_list if player not in paired_residents]
        pairs = sum(self._has_resident_match(resident) for resident in remainder) // 2

        self._homogeneous_s1 = remainder[:pairs]
        self._homogeneous_s2 = remainder[pairs:]

        for i, resident in enumerate(remainder):
            value = ((int(i < pairs) << (2 * self._bracket.bracket_bits)) - i) << 1
            self._bracket_matcher.add_to_weights(resident, remainder[i + 1:], value)

        self._bracket_matcher.update_matching()
        self._exchanges = sum(self._in_s2(resident) for resident in self._homogeneous_s1)

    def determine_moves_from_s1_to_s2(self) -> None:
        for i in range(len(self._homogeneous_s1) - 1, -1, -1):
            if self._exchanges == 0:
                return

            resident = self._homogeneous_s1[i]
            lower_residents = self._homogeneous_s1[i + 1:] + self._homogeneous_s2
            was_exchanged = self._in_s2(resident)

            if not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, lower_residents, -1)
                self._bracket_matcher.update_matching()

            if self._in_s2(resident):
                self._exchanges -= 1
                self._bracket_matcher.remove_weights(resident, lower_residents)

            elif not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, lower_residents, 1)

    def determine_moves_from_s2_to_s1(self) -> None:
        for i, resident in enumerate(self._homogeneous_s2):
            if self._exchanges == 0:
                return

            higher_residents = self._homogeneous_s1 + self._homogeneous_s2[i + 1:]
            was_exchanged = self._in_s1(resident)

            if not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, higher_residents, 1)
                self._bracket_matcher.update_matching()

            if self._in_s2(resident):
                self._exchanges -= 1
                self._bracket_matcher.remove_weights(resident, higher_residents[:-1] + self._bracket.lower_list)

            elif not was_exchanged:
                self._bracket_matcher.add_to_weights(resident, higher_residents, -1)

    def perform_homogeneous_exchanges(self) -> None:
        homogeneous_bracket = self._homogeneous_s1 + self._homogeneous_s2

        self._homogeneous_s1 = [resident for resident in homogeneous_bracket if self._in_s1(resident)]
        self._homogeneous_s2 = [resident for resident in homogeneous_bracket if self._in_s2(resident)]

        for i, resident in enumerate(self._homogeneous_s1):
            self._bracket_matcher.remove_weights(resident, self._homogeneous_s1[i + 1:])

        for i, resident in enumerate(self._homogeneous_s2):
            self._bracket_matcher.remove_weights(resident, self._homogeneous_s2[i + 1:])

    def transpose_homogeneous_s2(self) -> None:
        for resident in self._homogeneous_s1:
            self._bracket_matcher.add_to_weights(resident, self._homogeneous_s2[::-1], 0, increment=True)

            self._bracket_matcher.update_matching()
            match = self._bracket_matcher.matching[resident]
            self._bracket_matcher.finalize_match(resident, match)
            self._validity_matcher.finalize_match(resident, match)

    def check_completion_criterium(self) -> bool:
        if self._bracket.penultimate_pairing_bracket or self._bracket.last_pairing_bracket:
            return True
        return self._validity_matcher.is_valid_matching()

    def get_player_pairs(self) -> list[tuple[Player, Player]]:
        player_pairs = []

        for player_1, player_2 in self._bracket_matcher.matching.items():
            if player_1.role == PlayerRole.LOWER or player_2.role == PlayerRole.LOWER:
                continue
            if player_1 > player_2:
                player_pairs.append(self._get_player_pair(player_1, player_2))
            if player_1.number == player_2.number and self._bracket.last_pairing_bracket:
                player_pairs.append(self._get_player_pair(player_1, player_2))

        return player_pairs
