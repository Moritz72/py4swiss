from itertools import groupby

from py4swiss.dynamicuint import DynamicUint
from py4swiss.engines.common import ColorPreferenceSide, ColorPreferenceStrength, Float, Pairing
from py4swiss.engines.dutch.player_info import PlayerInfo, PlayerRole
from py4swiss.engines.dutch.validity_matcher import ValidityMatcher
from py4swiss.matching_computer import ComputerDutchOptimality


class BracketMatcher:
    def __init__(
            self,
            mdp_list: list[PlayerInfo],
            resident_list: list[PlayerInfo],
            low_resident_list: list[PlayerInfo],
            round_number: int,
            is_penultimate_pairing_bracket: bool,
            is_last_pairing_bracket: bool,
            validity_matcher: ValidityMatcher
    ) -> None:
        self.mdp_list: list[PlayerInfo] = mdp_list
        self.resident_list: list[PlayerInfo] = resident_list
        self.low_resident_list: list[PlayerInfo] = low_resident_list
        self.round_number: int = round_number
        self.is_penultimate_pairing_bracket: bool = is_penultimate_pairing_bracket
        self.is_last_pairing_bracket: bool = is_last_pairing_bracket
        self.validity_matcher: ValidityMatcher = validity_matcher

        self.full_list = self.mdp_list + self.resident_list + self.low_resident_list
        score_difference_bits = self._get_score_difference_bits(mdp_list, resident_list)
        self.score_difference_bit_dict: dict[int, int] = score_difference_bits[0]
        self.score_difference_total_bits: int = score_difference_bits[1]
        self.bracket_bits: int = len(resident_list).bit_length()
        self.low_bracket_bits: int = len(low_resident_list).bit_length()
        self.min_bracket_score: int = resident_list[-1].points

        self.num_mdp: int = len(self.mdp_list)
        self.num_resident: int = len(self.resident_list)
        self.num_lower: int = len(self.low_resident_list)
        self.num_total: int = len(self.full_list)

        self.max_weight: DynamicUint = self._get_max_weight()
        self.computer: ComputerDutchOptimality = ComputerDutchOptimality(len(self), self.max_weight)
        self.weights: list[list[DynamicUint]] = [[DynamicUint(0) for _ in range(len(self))] for _ in range(len(self))]
        self.matching: dict[PlayerInfo, PlayerInfo] = {}

        self.index_dict: dict[PlayerInfo, int] = {player: i for i, player in enumerate(self.full_list)}
        self.index_dict_reverse: dict[int, PlayerInfo] = {i: player for i, player in enumerate(self.full_list)}
        self.matched_dict: dict[PlayerInfo, bool] = {player: False for player in self.full_list}

        if self.num_total % 2 == 1:
            dummy_player = PlayerInfo.get_dummy()
            self.index_dict[dummy_player] = self.num_total
            self.index_dict_reverse[self.num_total] = dummy_player

        for _ in range(len(self)):
            self.computer.add_vertex()

    def __len__(self) -> int:
        return self.num_total + (self.num_total % 2)

    @staticmethod
    def _get_score_difference_bits(
            mdp_list: list[PlayerInfo],
            resident_list: list[PlayerInfo]
    ) -> tuple[dict[int, int], int]:
        point_differences = [player.points - resident_list[-1].points + 10 for player in mdp_list + resident_list]

        for mdp in mdp_list:
            point_differences.extend({mdp.points - resident.points for resident in resident_list})

        for i, resident in enumerate(resident_list):
            point_differences.extend({resident.points - other.points for other in resident_list[i + 1:]})

        bits = {key: point_differences.count(key).bit_length() for key in point_differences}
        cumulative_bits = {}
        running_total = 0

        for key in sorted(bits):
            cumulative_bits[key] = running_total
            running_total += bits[key]

        return cumulative_bits, running_total

    @staticmethod
    def _is_white_pair(player_1: PlayerInfo, player_2: PlayerInfo, initial_white: bool) -> bool:
        # E.1
        exists = player_1.color_preference.side and player_2.color_preference.side
        no_conflict = player_1.color_preference.side != player_2.color_preference.side
        if exists and no_conflict:
            return player_1.color_preference.side == ColorPreferenceSide.WHITE

        # E.2
        is_same_strength = player_1.color_preference.strength == player_2.color_preference.strength
        is_same_difference = abs(player_1.color_difference) == abs(player_2.color_difference)
        is_absolute = all(p.color_preference.strength == ColorPreferenceStrength.ABSOLUTE for p in (player_1, player_2))
        if not is_same_strength:
            if player_1.color_preference.strength > player_2.color_preference.strength:
                return player_1.color_preference.side == ColorPreferenceSide.WHITE
            return player_2.color_preference.side == ColorPreferenceSide.BLACK
        if is_absolute and not is_same_difference:
            if abs(player_1.color_difference) > abs(player_2.color_difference):
                return player_1.color_preference.side == ColorPreferenceSide.WHITE
            return player_2.color_preference.side == ColorPreferenceSide.BLACK

        # E.3
        colors_1 = [color for color in player_1.colors if color is not None]
        colors_2 = [color for color in player_2.colors if color is not None]
        for color_1, color_2 in zip(colors_1[::-1], colors_2[::-1]):
            if color_1 != color_2:
                return not color_1

        # E.4
        if player_1 > player_2 and bool(player_1.color_preference.side):
            return player_1.color_preference.side == ColorPreferenceSide.WHITE
        if player_2 > player_1 and bool(player_2.color_preference.side):
            return player_2.color_preference.side == ColorPreferenceSide.BLACK

        # E.5
        if player_1.number < player_2.number:
            return bool(player_1.number % 2) and initial_white
        return not (bool(player_2.number % 2) and initial_white)

    def _compute_matching(self) -> None:
        self.computer.compute_matching()
        self.matching = {
            self.index_dict_reverse[i]: self.index_dict_reverse[j]
            for i, j in enumerate(self.computer.get_matching()[:self.num_total])
        }

    def _add_to_weight(self, player: PlayerInfo, opponent: PlayerInfo, value: int) -> None:
        i = self.index_dict[player]
        j = self.index_dict[opponent]
        weight = self.weights[i][j]
        if bool(weight):
            if value > 0:
                plus_weight = self.max_weight.get_empty()
                plus_weight |= value
                weight += plus_weight
            else:
                plus_weight = self.max_weight.get_empty()
                plus_weight |= -value
                weight -= plus_weight
        self.computer.set_edge_weight(i, j, weight)

    def _remove_weight(self, player: PlayerInfo, opponent: PlayerInfo) -> None:
        i = self.index_dict[player]
        j = self.index_dict[opponent]
        self.weights[i][j] &= 0
        self.computer.set_edge_weight(i, j, self.weights[i][j])

    def _finalize_match(self, player: PlayerInfo, opponent: PlayerInfo) -> None:
        i = self.index_dict[player]
        j = self.index_dict[opponent]
        for k in range(len(self)):
            self.weights[i][k] &= 0
            self.weights[k][i] &= 0
            self.computer.set_edge_weight(i, k, self.max_weight.get_empty())
            self.computer.set_edge_weight(k, i, self.max_weight.get_empty())
        for k in range(len(self)):
            self.weights[j][k] &= 0
            self.weights[k][j] &= 0
            self.computer.set_edge_weight(j, k, self.max_weight.get_empty())
            self.computer.set_edge_weight(k, j, self.max_weight.get_empty())
        self.weights[i][j] = self.max_weight
        self.computer.set_edge_weight(i, j, self.weights[i][j])

    def _get_max_weight(self) -> DynamicUint:
        weight = DynamicUint(0)
        if self.special:
            weight |= 2  # C.4
        weight.shift_grow(self.bracket_bits)  # C.5
        weight |= int(not bool(weight))
        weight.shift_grow(self.score_difference_total_bits)  # C.6
        if not self.special:
            weight.shift_grow(self.low_bracket_bits)  # C.7
            weight.shift_grow(self.score_difference_total_bits)  # C.7
        weight.shift_grow(self.bracket_bits)  # C.8
        weight.shift_grow(self.bracket_bits)  # C.9
        weight.shift_grow(self.bracket_bits)  # C.10
        weight.shift_grow(self.bracket_bits)  # C.11
        if self.round_number > 1:
            weight.shift_grow(self.bracket_bits)  # C.12
            weight.shift_grow(self.bracket_bits)  # C.13
        if self.round_number > 2:
            weight.shift_grow(self.bracket_bits)  # C.14
            weight.shift_grow(self.bracket_bits)  # C.15
        if self.round_number > 1:
            weight.shift_grow(self.score_difference_total_bits)  # C.16
            weight.shift_grow(self.score_difference_total_bits)  # C.17
        if self.round_number > 2:
            weight.shift_grow(self.score_difference_total_bits)  # C.18
            weight.shift_grow(self.score_difference_total_bits)  # C.19
        weight.shift_grow(self.bracket_bits)  # D.1 - D.3
        weight.shift_grow(self.bracket_bits)  # D.1 - D.3
        weight.shift_grow(self.bracket_bits)  # D.1 - D.3
        weight.shift_grow(1)  # D.1 - D.3

        weight.shift_grow(2)
        weight >>= 1
        subtract = weight.get_empty()
        subtract |= 1
        weight -= subtract
        return weight

    @property
    def special(self) -> bool:
        return self.is_penultimate_pairing_bracket or self.is_last_pairing_bracket

    def get_base_weight(self, player_1: PlayerInfo, player_2: PlayerInfo) -> DynamicUint:
        weight = self.max_weight.get_empty()
        if not ValidityMatcher.is_allowed_pairing(player_1, player_2):
            return weight

        # C.4
        if self.special:
            weight |= 1 + player_1.bye_received + player_2.bye_received

        # C.5
        weight <<= self.bracket_bits
        weight |= int(not player_2.role == PlayerRole.LOWER)

        # C.6
        weight <<= self.score_difference_total_bits
        if not player_2.role == PlayerRole.LOWER:
            difference_1 = player_1.points - self.min_bracket_score + 10
            difference_2 = player_2.points - self.min_bracket_score + 10
            difference_3 = player_1.points - player_2.points
            weight += (weight.get_empty() | 1) << self.score_difference_bit_dict[difference_1]
            weight += (weight.get_empty() | 1) << self.score_difference_bit_dict[difference_2]
            weight -= (weight.get_empty() | 1) << self.score_difference_bit_dict.get(difference_3, 0)

        # C.7
        if not self.special:
            weight <<= self.low_bracket_bits
            weight |= int(player_2.role == PlayerRole.LOWER)
            weight <<= self.score_difference_total_bits
            if not player_1.role == PlayerRole.LOWER:
                difference = player_1.points - self.min_bracket_score + 10
                weight += (weight.get_empty() | 1) << self.score_difference_bit_dict[difference]
            if not player_2.role == PlayerRole.LOWER:
                difference = player_2.points - self.min_bracket_score + 10
                weight += (weight.get_empty() | 1) << self.score_difference_bit_dict[difference]

        # C.8
        weight <<= self.bracket_bits
        if not player_2.role == PlayerRole.LOWER:
            topscorer = player_1.top_scorer or player_2.top_scorer
            at_least_2 = abs(player_1.color_difference) > 1 and abs(player_2.color_difference) > 1
            conflict = player_1.color_preference.side == player_2.color_preference.side
            weight |= int(not (topscorer and at_least_2 and conflict))

        # C.9
        weight <<= self.bracket_bits
        if not player_2.role == PlayerRole.LOWER:
            topscorer = player_1.top_scorer or player_2.top_scorer
            double = player_1.color_double and player_2.color_double
            conflict = player_1.color_preference.side == player_2.color_preference.side
            weight |= int(not (topscorer and double and conflict))

        # C.10
        weight <<= self.bracket_bits
        if not player_2.role == PlayerRole.LOWER:
            conflict = player_1.color_preference.side == player_2.color_preference.side
            weight |= int(not conflict)

        # C.11
        weight <<= self.bracket_bits
        if not player_2.role == PlayerRole.LOWER:
            strong = all(p.color_preference.strength >= ColorPreferenceStrength.STRONG for p in (player_1, player_2))
            conflict = player_1.color_preference.side == player_2.color_preference.side
            weight |= int(not (strong and conflict))

        # C.12
        if self.round_number > 1:
            weight <<= self.bracket_bits
            if not player_2.role == PlayerRole.LOWER:
                prevented_double_float_1 = (player_1.float_1 == Float.DOWN) and (player_1.points <= player_2.points)
                prevented_double_float_2 = player_2.float_1 == Float.DOWN
                weight |= int(prevented_double_float_1) + int(prevented_double_float_2)

        # C.13
        if self.round_number > 1:
            weight <<= self.bracket_bits
            if not player_2.role == PlayerRole.LOWER:
                double = (player_2.float_1 == Float.UP) and (player_1.points > player_2.points)
                weight |= int(not double)

        # C.14
        if self.round_number > 2:
            weight <<= self.bracket_bits
            if not player_2.role == PlayerRole.LOWER:
                prevented_double_float_1 = (player_1.float_2 == Float.DOWN) and (player_1.points <= player_2.points)
                prevented_double_float_2 = player_2.float_2 == Float.DOWN
                weight |= int(prevented_double_float_1) + int(prevented_double_float_2)

        # C.15
        if self.round_number > 2:
            weight <<= self.bracket_bits
            if not player_2.role == PlayerRole.LOWER:
                double = (player_2.float_2 == Float.UP) and (player_1.points > player_2.points)
                weight |= int(not double)

        # C.16
        if self.round_number > 1:
            weight <<= self.score_difference_total_bits
            if not player_2.role == PlayerRole.LOWER:
                prev_1 = player_1.float_1 == Float.DOWN
                prev_2 = player_2.float_1 == Float.DOWN
                difference_1 = player_1.points - self.min_bracket_score + 10
                difference_2 = player_2.points - self.min_bracket_score + 10
                weight += (weight.get_empty() | int(prev_1)) << self.score_difference_bit_dict[difference_1]
                weight += (weight.get_empty() | int(prev_2)) << self.score_difference_bit_dict[difference_2]
                if prev_1 and player_1.points > player_2.points:
                    difference_3 = player_1.points - player_2.points
                    weight -= (weight.get_empty() | 1) << self.score_difference_bit_dict.get(difference_3, 0)

        # C.17
        if self.round_number > 1:
            weight <<= self.score_difference_total_bits
            if not player_2.role == PlayerRole.LOWER:
                double = (player_2.float_1 == Float.UP) and (player_1.points > player_2.points)
                difference = player_1.points - self.min_bracket_score + 10
                weight -= (weight.get_empty() | int(double)) << self.score_difference_bit_dict[difference]

        # C.18
        if self.round_number > 2:
            weight <<= self.score_difference_total_bits
            if not player_2.role == PlayerRole.LOWER:
                prev_1 = player_1.float_2 == Float.DOWN
                prev_2 = player_2.float_2 == Float.DOWN
                difference_1 = player_1.points - self.min_bracket_score + 10
                difference_2 = player_2.points - self.min_bracket_score + 10
                difference_3 = player_1.points - player_2.points
                weight += (weight.get_empty() | int(prev_1)) << self.score_difference_bit_dict[difference_1]
                weight += (weight.get_empty() | int(prev_2)) << self.score_difference_bit_dict[difference_2]
                if prev_1 and player_1.points > player_2.points:
                    weight -= (weight.get_empty() | 1) << self.score_difference_bit_dict.get(difference_3, 0)

        # C.19
        if self.round_number > 2:
            weight <<= self.score_difference_total_bits
            if not player_2.role == PlayerRole.LOWER:
                double = (player_2.float_2 == Float.UP) and (player_1.points > player_2.points)
                difference = player_1.points - self.min_bracket_score + 10
                weight -= (weight.get_empty() | int(double)) << self.score_difference_bit_dict[difference]

        # D.1 - D.3 (provisional)
        weight <<= self.bracket_bits
        weight <<= self.bracket_bits
        weight <<= self.bracket_bits
        weight <<= 1

        return weight

    def calculate_base_matching(self) -> None:
        for i, player_1 in enumerate(self.full_list):
            for j, player_2 in enumerate(self.full_list[i + 1:]):
                weight = self.get_base_weight(player_1, player_2)
                self.weights[i][i + j + 1] = weight
                self.computer.set_edge_weight(i, i + j + 1, weight)
        self._compute_matching()

    def finalize_mdp_matches(self) -> None:
        is_match_to_resident_dict = {
            mdp: self.matching[mdp].role == PlayerRole.RESIDENT
            for i, mdp in enumerate(self.mdp_list)
        }

        groups = [list(group) for score, group in groupby(self.mdp_list, key=lambda mdp: mdp.points)]
        groups = [group for group in groups if any(is_match_to_resident_dict[mdp] for mdp in group)]

        for group in groups:
            for mdp in group:
                if not self.matching[mdp].role == PlayerRole.RESIDENT:
                    for resident in self.resident_list:
                        self._add_to_weight(mdp, resident, 1)
                    self._compute_matching()

                if self.matching[mdp].role == PlayerRole.RESIDENT:
                    self.matched_dict[mdp] = True
                    for resident in self.resident_list:
                        self._add_to_weight(mdp, resident, self.num_resident + 1)

        for mdp_player in self.mdp_list:
            if not self.matched_dict[mdp_player]:
                continue
            added_value = self.num_total

            for resident_player in self.resident_list[::-1]:
                if self.matched_dict[resident_player]:
                    continue
                self._add_to_weight(mdp_player, resident_player, added_value)
                added_value += 1

            self._compute_matching()
            matched_resident = self.matching[mdp_player]
            self.matched_dict[matched_resident] = True
            self._finalize_match(mdp_player, matched_resident)
            self.validity_matcher.finalize_match(mdp_player, matched_resident)

    def finalize_resident_matches(self) -> None:
        remainder = [player for player in self.resident_list if not self.matched_dict[player]]
        pairs = sum(self.matching[resident].role == PlayerRole.RESIDENT for resident in remainder) // 2
        original_s_1 = remainder[:pairs]
        original_s_2 = remainder[pairs:]

        for i, resident_1 in enumerate(remainder):
            for resident_2 in remainder[i + 1:]:
                added_value = int(i < pairs)
                added_value <<= self.bracket_bits
                added_value <<= self.bracket_bits
                added_value -= i
                added_value <<= 1
                self._add_to_weight(resident_1, resident_2, added_value)

        self._compute_matching()
        exchanges = sum(
            resident < self.matching[resident] or self.matching[resident].role == PlayerRole.LOWER
            for resident in original_s_1
        )

        for i in range(len(original_s_1) - 1, -1, -1):
            if exchanges == 0:
                break

            resident = original_s_1[i]
            was_exchanged = resident < self.matching[resident] or self.matching[resident].role == PlayerRole.LOWER

            if not was_exchanged:
                for resident_lower in remainder[i + 1:]:
                    self._add_to_weight(resident, resident_lower, -1)
                self._compute_matching()

            now_exchanged = resident < self.matching[resident] or self.matching[resident].role == PlayerRole.LOWER
            exchanges -= int(now_exchanged)

            if now_exchanged:
                for resident_lower in remainder[i + 1:]:
                    self._remove_weight(resident, resident_lower)
            elif not was_exchanged:
                for resident_lower in remainder[i + 1:]:
                    self._add_to_weight(resident, resident_lower, 1)

        for i, resident in enumerate(original_s_2):
            if exchanges == 0:
                break

            was_exchanged = resident > self.matching[resident] and self.matching[resident].role == PlayerRole.RESIDENT

            if not was_exchanged:
                for resident_higher in remainder[i + 1:]:
                    self._add_to_weight(resident_higher, resident, 1)
                self._compute_matching()

            now_exchanged = resident < self.matching[resident] or self.matching[resident].role == PlayerRole.LOWER
            exchanges -= int(now_exchanged)

            if now_exchanged:
                for resident_higher in remainder[:i]:
                    self._remove_weight(resident_higher, resident)
                for low_resident in self.low_resident_list:
                    self._remove_weight(resident, low_resident)
            elif not was_exchanged:
                for resident_lower in remainder[i + 1:]:
                    self._add_to_weight(resident, resident_lower, -1)

        for i, resident in enumerate(remainder):
            for resident_lower in remainder[i + 1:]:
                match = self.matching[resident]
                match_lower = self.matching[resident_lower]
                if match > resident or match.role == PlayerRole.LOWER:
                    self._remove_weight(resident, resident_lower)
                if match_lower < resident_lower and match_lower.role == PlayerRole.RESIDENT:
                    self._remove_weight(resident, resident_lower)

        for i, resident in enumerate(remainder):
            if self.matching[resident] >= resident or self.matching[resident].role == PlayerRole.LOWER:
                continue
            for added_value, resident_lower in enumerate(remainder[:i:-1]):
                self._add_to_weight(resident, resident_lower, added_value)

            self._compute_matching()
            match = self.matching[resident]
            self._finalize_match(resident, match)
            self.validity_matcher.finalize_match(resident, match)

    def check_completion_criterium(self) -> bool:
        if self.special:
            return True
        return self.validity_matcher.is_valid_matching()

    def get_pairings(self) -> list[Pairing]:
        pairings = []

        for player_1, player_2 in self.matching.items():
            if player_1.role == PlayerRole.LOWER or player_2.role == PlayerRole.LOWER or player_2 > player_1:
                continue
            if player_1.number == player_2.number:
                if self.is_last_pairing_bracket:
                    pairings.append(Pairing(white=player_1.number, black=0))
                continue
            is_white_pair = self._is_white_pair(player_1, player_2, True)

            if is_white_pair:
                pairings.append(Pairing(white=player_1.number, black=player_2.number))
            else:
                pairings.append(Pairing(white=player_2.number, black=player_1.number))

        return pairings
